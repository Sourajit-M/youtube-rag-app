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
from youtube import get_transcript


model = SentenceTransformer(EMBEDDING_MODEL)

client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)


def create_collection():
    if client.collection_exists(COLLECTION_NAME):
        return

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


def ingest_video(video_id, video_title=None, playlist_id=None):
    print("Fetching transcript...")

    transcript = get_transcript(video_id)

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

    print("Uploading to Qdrant...")

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
    )

    print(f"Uploaded {len(points)} chunks.")

    return len(points)


if __name__ == "__main__":
    video_id = input("Enter YouTube video ID: ")

    create_collection()

    ingest_video(video_id)