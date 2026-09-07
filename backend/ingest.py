from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

from config import (
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    QDRANT_API_KEY,
    QDRANT_URL,
)
from chunking import create_chunks
from youtube import (
    get_playlist_videos,
    get_transcript,
)


model = SentenceTransformer(EMBEDDING_MODEL)

client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)


def create_collection():
    if not client.collection_exists(COLLECTION_NAME):
        vector_size = model.get_embedding_dimension()

        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE,
            ),
        )

        print(f"Created collection: {COLLECTION_NAME}")
        print(f"Vector size: {vector_size}")

    try:
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="video_id",
            field_schema="keyword",
        )
    except Exception:
        pass

    try:
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="playlist_id",
            field_schema="keyword",
        )
    except Exception:
        pass

def video_already_exists(video_id):
    results = client.scroll(
        collection_name=COLLECTION_NAME,
        scroll_filter={
            "must": [
                {
                    "key": "video_id",
                    "match": {
                        "value": video_id,
                    },
                }
            ]
        },
        limit=1,
    )

    points, _ = results

    return len(points) > 0


def ingest_video(
    video_id,
    video_title=None,
    playlist_id=None,
):
    if video_already_exists(video_id):
        print(f"Skipping {video_id}: already indexed.")
        return 0

    print(f"\nProcessing: {video_title or video_id}")

    try:
        transcript = get_transcript(video_id)
    except Exception as e:
        print(f"Could not get transcript: {e}")
        return 0

    print(f"Transcript segments: {len(transcript)}")

    chunks = create_chunks(transcript)

    print(f"Created chunks: {len(chunks)}")

    texts = [chunk["text"] for chunk in chunks]

    print("Generating embeddings...")

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    points = []

    for chunk, embedding in zip(chunks, embeddings):
        points.append(
            PointStruct(
                id=str(uuid4()),
                vector=embedding.tolist(),
                payload={
                    "video_id": video_id,
                    "video_title": video_title,
                    "playlist_id": playlist_id,
                    "text": chunk["text"],
                    "start_time": chunk["start_time"],
                    "end_time": chunk["end_time"],
                },
            )
        )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
    )

    print(f"Uploaded {len(points)} chunks.")

    return len(points)


def ingest_playlist(playlist_url):
    playlist_id, videos = get_playlist_videos(
        playlist_url
    )

    print(f"Playlist ID: {playlist_id}")
    print(f"Videos found: {len(videos)}")

    total_chunks = 0
    successful_videos = 0
    failed_videos = []

    for index, video in enumerate(videos, start=1):
        video_id = video["video_id"]
        video_title = video["video_title"]

        print(
            f"\n========== "
            f"{index}/{len(videos)} =========="
        )

        chunks = ingest_video(
            video_id=video_id,
            video_title=video_title,
            playlist_id=playlist_id,
        )

        if chunks > 0:
            successful_videos += 1
            total_chunks += chunks
        elif not video_already_exists(video_id):
            failed_videos.append(
                {
                    "video_id": video_id,
                    "video_title": video_title,
                }
            )

    print("\n========== PLAYLIST COMPLETE ==========")
    print(f"Videos found: {len(videos)}")
    print(f"Videos indexed: {successful_videos}")
    print(f"Total chunks: {total_chunks}")

    if failed_videos:
        print("\nVideos that could not be indexed:")

        for video in failed_videos:
            print(
                f'- {video["video_title"]} '
                f'({video["video_id"]})'
            )


if __name__ == "__main__":
    create_collection()

    url = input(
        "Enter YouTube video or playlist URL: "
    )

    if "playlist" in url:
        ingest_playlist(url)
    else:
        video_id = get_video_id(url)

        ingest_video(video_id)