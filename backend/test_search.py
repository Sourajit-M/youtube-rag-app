from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

from config import (
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    QDRANT_API_KEY,
    QDRANT_URL,
)


model = SentenceTransformer(EMBEDDING_MODEL)

client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)


question = input("Ask a question: ")

query_embedding = model.encode(
    question,
    normalize_embeddings=True,
)


results = client.query_points(
    collection_name=COLLECTION_NAME,
    query=query_embedding.tolist(),
    limit=5,
).points


for i, result in enumerate(results, start=1):
    print(f"\n--- RESULT {i} ---")
    print("Score:", result.score)
    print("Video:", result.payload["video_title"])
    print("Start:", result.payload["start_time"])
    print("End:", result.payload["end_time"])
    print("Text:", result.payload["text"][:500])