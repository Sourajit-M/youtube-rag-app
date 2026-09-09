import os
import sys
from pathlib import Path
from typing import List, Dict, Optional


from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
from fastembed import SparseTextEmbedding

from backend.config import (
    QDRANT_URL,
    QDRANT_API_KEY,
    COLLECTION_NAME,
    DENSE_MODEL_NAME,
    SPARSE_MODEL_NAME,
    TOP_K_DEFAULT,
)

# Shared clients and models
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
dense_model = SentenceTransformer(DENSE_MODEL_NAME)
sparse_model = SparseTextEmbedding(model_name=SPARSE_MODEL_NAME)


def format_seconds(seconds: int) -> str:
    """Converts seconds into HH:MM:SS or MM:SS format."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def hybrid_search(
    query: str,
    top_k: int = TOP_K_DEFAULT,
) -> List[Dict]:
    """
    Performs Native Qdrant Cloud Hybrid Search across all stored videos in the DB:
    Fuses Dense Vector Search + BM25 Sparse Vector Search using server-side RRF.
    """
    # 1. Encode query
    dense_vec = dense_model.encode(query)
    sparse_vec = list(sparse_model.embed([query]))[0]

    # 2. Server-side Reciprocal Rank Fusion (RRF) in Qdrant Cloud
    prefetch_limit = max(top_k * 3, 10)
    response = client.query_points(
        collection_name=COLLECTION_NAME,
        prefetch=[
            models.Prefetch(
                query=dense_vec.tolist(),
                using="dense",
                limit=prefetch_limit,
            ),
            models.Prefetch(
                query=models.SparseVector(
                    indices=sparse_vec.indices.tolist(),
                    values=sparse_vec.values.tolist(),
                ),
                using="sparse",
                limit=prefetch_limit,
            ),
        ],
        query=models.FusionQuery(fusion=models.Fusion.RRF),
        limit=top_k,
    )

    results = []
    for point in response.points:
        payload = point.payload or {}
        v_id = payload.get("video_id", "")
        start_time = payload.get("start_time", 0)

        results.append({
            "score": round(float(point.score), 4),
            "video_id": v_id,
            "video_title": payload.get("video_title", ""),
            "playlist_id": payload.get("playlist_id", ""),
            "start_time": start_time,
            "timestamp_formatted": format_seconds(start_time),
            "youtube_url": f"https://youtube.com/watch?v={v_id}&t={start_time}s",
            "text": payload.get("text", ""),
            "text_original": payload.get("text_original", ""),
            "lang_original": payload.get("lang_original", "en"),
        })

    return results


def get_indexed_videos() -> List[Dict]:
    """
    Returns unique indexed videos with their titles, chunk count, and playlist IDs.
    """
    try:
        if not client.collection_exists(COLLECTION_NAME):
            return []

        videos_map = {}
        offset = None

        # Scroll through points to aggregate unique videos
        while True:
            records, next_offset = client.scroll(
                collection_name=COLLECTION_NAME,
                limit=250,
                offset=offset,
                with_payload=True,
                with_vectors=False,
            )
            for r in records:
                p = r.payload or {}
                vid = p.get("video_id")
                if vid:
                    if vid not in videos_map:
                        videos_map[vid] = {
                            "video_id": vid,
                            "video_title": p.get("video_title", vid),
                            "playlist_id": p.get("playlist_id", ""),
                            "chunk_count": 0,
                            "lang_original": p.get("lang_original", "en"),
                        }
                    videos_map[vid]["chunk_count"] += 1

            if next_offset is None:
                break
            offset = next_offset

        return list(videos_map.values())
    except Exception as e:
        print(f"[Warn] Failed to list indexed videos: {e}")
        return []


if __name__ == "__main__":
    test_q = "What is polymorphism and inheritance?"
    print(f"Executing hybrid search for query: '{test_q}'\n")
    hits = hybrid_search(test_q, top_k=3)
    for i, h in enumerate(hits, 1):
        print(f"[{i}] RRF Score: {h['score']} | {h['video_title']} @ {h['timestamp_formatted']}")
        print(f"    Link: {h['youtube_url']}")
        print(f"    Context: {h['text'][:140]}...\n")

    print("\nIndexed Videos:", get_indexed_videos())
