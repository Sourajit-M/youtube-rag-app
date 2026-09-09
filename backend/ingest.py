import os
import sys
import uuid
from pathlib import Path
from typing import List, Dict, Tuple, Optional


from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
from fastembed import SparseTextEmbedding
from deep_translator import GoogleTranslator
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp

from backend.config import (
    QDRANT_URL,
    QDRANT_API_KEY,
    COLLECTION_NAME,
    DENSE_MODEL_NAME,
    DENSE_VECTOR_SIZE,
    SPARSE_MODEL_NAME,
    CHUNK_WINDOW_SECONDS,
    CHUNK_OVERLAP_SECONDS,
)

# Shared clients and models
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
dense_model = SentenceTransformer(DENSE_MODEL_NAME)
sparse_model = SparseTextEmbedding(model_name=SPARSE_MODEL_NAME)
translator = GoogleTranslator(source="auto", target="en")


def setup_qdrant() -> None:
    """Ensures Qdrant collection exists with dense and sparse vectors."""
    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config={
                "dense": models.VectorParams(
                    size=DENSE_VECTOR_SIZE,
                    distance=models.Distance.COSINE,
                )
            },
            sparse_vectors_config={
                "sparse": models.SparseVectorParams(
                    modifier=models.Modifier.IDF
                )
            },
        )
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="video_id",
            field_schema=models.PayloadSchemaType.KEYWORD,
        )
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="playlist_id",
            field_schema=models.PayloadSchemaType.KEYWORD,
        )
        print(f"[Qdrant] Collection initialized: {COLLECTION_NAME}")


def is_video_ingested(video_id: str) -> bool:
    """Checks if a video_id has already been indexed in Qdrant."""
    setup_qdrant()
    res = client.scroll(
        collection_name=COLLECTION_NAME,
        scroll_filter=models.Filter(
            must=[models.FieldCondition(key="video_id", match=models.MatchValue(value=video_id))]
        ),
        limit=1,
    )
    return len(res[0]) > 0


def extract_youtube_info(url: str) -> Tuple[List[Dict[str, str]], Optional[str]]:
    """
    Extracts video ID, title, and optional playlist ID from a URL using yt-dlp.
    Returns: (list_of_videos, playlist_id)
    """
    ydl_opts = {
        "extract_flat": True,
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if not info:
            raise ValueError(f"Could not extract info from URL: {url}")

        videos = []
        playlist_id = None
        if info.get("_type") == "playlist" or "entries" in info:
            playlist_id = info.get("id")
            for entry in info.get("entries", []):
                if entry and entry.get("id"):
                    videos.append({
                        "video_id": entry.get("id"),
                        "title": entry.get("title") or entry.get("id"),
                        "playlist_id": playlist_id,
                    })
        else:
            video_id = info.get("id")
            title = info.get("title") or video_id
            videos.append({
                "video_id": video_id,
                "title": title,
                "playlist_id": None,
            })

        return videos, playlist_id


def fetch_transcript(video_id: str) -> Tuple[List[Dict], str]:
    """
    Fetches transcript using youtube-transcript-api.
    Prefers English transcripts, otherwise falls back to available language.
    Returns: (normalized_transcript_list, language_code)
    """
    ytt_api = YouTubeTranscriptApi()
    transcript_list = ytt_api.list(video_id)

    # 1. Try English first
    for lang_code in ["en", "en-US", "en-GB"]:
        try:
            t = transcript_list.find_transcript([lang_code])
            raw_entries = t.fetch()
            return normalize_transcript(raw_entries), "en"
        except Exception:
            pass

    # 2. Pick the first available transcript
    for t in transcript_list:
        raw_entries = t.fetch()
        return normalize_transcript(raw_entries), t.language_code

    raise RuntimeError(f"No transcript found for video {video_id}")


def normalize_transcript(raw_entries: list) -> List[Dict]:
    """Ensures each transcript entry is a dict with text, start, duration."""
    normalized = []
    for item in raw_entries:
        if isinstance(item, dict):
            normalized.append({
                "text": str(item.get("text", "")).strip(),
                "start": float(item.get("start", 0.0)),
                "duration": float(item.get("duration", 0.0)),
            })
        else:
            normalized.append({
                "text": str(getattr(item, "text", "")).strip(),
                "start": float(getattr(item, "start", 0.0)),
                "duration": float(getattr(item, "duration", 0.0)),
            })
    return normalized


def chunk_transcript(
    transcript: List[Dict],
    window_size: int = CHUNK_WINDOW_SECONDS,
    overlap: int = CHUNK_OVERLAP_SECONDS,
) -> List[Dict]:
    """
    Merges transcript segments into ~30-45s chunks.
    Crucial: anchors start_time strictly to the first segment's start time in that chunk.
    """
    chunks = []
    if not transcript:
        return chunks

    first_start = transcript[0]["start"]
    current_chunk = {"text": "", "start_time": first_start}
    current_end = first_start + window_size

    for entry in transcript:
        s = entry["start"]
        t = entry["text"]

        if s < current_end:
            current_chunk["text"] += (" " if current_chunk["text"] else "") + t
        else:
            if current_chunk["text"].strip():
                chunks.append(current_chunk)
            next_start = max(0.0, s - overlap)
            current_chunk = {"text": t, "start_time": s}
            current_end = next_start + window_size

    if current_chunk["text"].strip():
        chunks.append(current_chunk)

    return chunks


def translate_chunks_to_english(raw_chunks: List[Dict], source_lang: str = "auto", batch_size: int = 20) -> List[str]:
    """Translates chunks to English in batches using deep-translator."""
    texts = [c["text"].strip() for c in raw_chunks]
    translated_all = []
    translator = GoogleTranslator(source=source_lang if source_lang else "auto", target="en")

    print(f"[Translate] Translating {len(texts)} chunks ({source_lang} -> en)...")
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        try:
            translated_batch = translator.translate_batch(batch)
            translated_all.extend(translated_batch)
        except Exception:
            for text in batch:
                try:
                    translated_all.append(translator.translate(text))
                except Exception:
                    translated_all.append(text)

    return translated_all


def ingest_single_video(
    video_id: str,
    video_title: str,
    playlist_id: Optional[str] = None,
    force: bool = False,
) -> Dict:
    """
    Ingests a single video: extracts transcript, chunks, translates,
    computes dense + sparse embeddings, and upserts to Qdrant Cloud.
    """
    setup_qdrant()

    if not force and is_video_ingested(video_id):
        print(f"[Skip] Video already ingested: {video_id} ({video_title})")
        return {"video_id": video_id, "title": video_title, "status": "already_indexed", "chunks": 0}

    print(f"\n[Ingest] Processing video: {video_id} ({video_title})")
    raw_transcript, lang = fetch_transcript(video_id)
    chunks = chunk_transcript(raw_transcript)

    if not chunks:
        print(f"[Warn] No chunks generated for video: {video_id}")
        return {"video_id": video_id, "title": video_title, "status": "no_transcript", "chunks": 0}

    # Translate if non-English
    if lang != "en":
        english_texts = translate_chunks_to_english(chunks, source_lang=lang)
    else:
        english_texts = [c["text"].strip() for c in chunks]

    # Compute dense embeddings
    print(f"[Dense Embed] Computing dense embeddings for {len(english_texts)} chunks...")
    dense_embeddings = dense_model.encode(english_texts, batch_size=32, show_progress_bar=False)

    # Compute sparse embeddings (fastembed BM25)
    print(f"[Sparse Embed] Computing sparse BM25 vectors for {len(english_texts)} chunks...")
    sparse_embeddings = list(sparse_model.embed(english_texts))

    points = []
    for chunk, eng_text, dense_vec, sparse_vec in zip(
        chunks, english_texts, dense_embeddings, sparse_embeddings
    ):
        point_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{video_id}_{chunk['start_time']}"))
        points.append(
            models.PointStruct(
                id=point_id,
                vector={
                    "dense": dense_vec.tolist(),
                    "sparse": models.SparseVector(
                        indices=sparse_vec.indices.tolist(),
                        values=sparse_vec.values.tolist(),
                    ),
                },
                payload={
                    "video_id": video_id,
                    "video_title": video_title,
                    "playlist_id": playlist_id or "",
                    "start_time": int(chunk["start_time"]),
                    "text": eng_text,
                    "text_original": chunk["text"],
                    "lang_original": lang,
                },
            )
        )

    # Upsert in batches of 100
    for i in range(0, len(points), 100):
        client.upsert(collection_name=COLLECTION_NAME, points=points[i : i + 100])

    print(f"[Success] Upserted {len(points)} points for video: {video_id}")
    return {"video_id": video_id, "title": video_title, "status": "success", "chunks": len(points)}


def ingest_url(url: str, force: bool = False) -> List[Dict]:
    """Ingests a video or full playlist from a YouTube URL."""
    videos, playlist_id = extract_youtube_info(url)
    print(f"[Ingest URL] Found {len(videos)} video(s) to process.")
    results = []
    for v in videos:
        try:
            res = ingest_single_video(
                video_id=v["video_id"],
                video_title=v["title"],
                playlist_id=v.get("playlist_id"),
                force=force,
            )
            results.append(res)
        except Exception as e:
            print(f"[Error] Failed to ingest video {v['video_id']}: {e}")
            results.append({
                "video_id": v["video_id"],
                "title": v.get("title", v["video_id"]),
                "status": f"error: {str(e)}",
                "chunks": 0,
            })
    return results


if __name__ == "__main__":
    import sys
    test_url = sys.argv[1] if len(sys.argv) > 1 else "46T2wD3IuhM"
    results = ingest_url(test_url, force=True)
    print("\nIngestion Summary:", results)
