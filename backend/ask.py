import os

from groq import Groq
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

from config import (
    COLLECTION_NAME,
    EMBEDDING_MODEL,
    QDRANT_API_KEY,
    QDRANT_URL,
    GROQ_API_KEY,
    GROQ_MODEL
)


model = SentenceTransformer(EMBEDDING_MODEL)

qdrant = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)

groq = Groq(
    api_key=GROQ_API_KEY
)


def search(question, limit=5):
    query_embedding = model.encode(
        question,
        normalize_embeddings=True,
    )

    results = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding.tolist(),
        limit=limit,
    ).points

    return results


def format_timestamp(seconds):
    seconds = int(seconds)

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    return f"{minutes:02d}:{seconds:02d}"


def create_youtube_url(video_id, start_time):
    return (
        f"https://www.youtube.com/watch?v={video_id}"
        f"&t={int(start_time)}s"
    )


def generate_answer(question, results):
    context = ""

    for i, result in enumerate(results, start=1):
        payload = result.payload

        context += f"""
SOURCE {i}

Video ID: {payload["video_id"]}
Start time: {payload["start_time"]}
End time: {payload["end_time"]}

Text:
{payload["text"]}

---
"""

    prompt = f"""
You are a helpful assistant answering questions about YouTube videos.

Answer the question using ONLY the provided context.

If the answer cannot be found in the context, say:
"I couldn't find that information in the video."

Do not use outside knowledge.
Do not make up information.

Answer in English.

Question:
{question}

Context:
{context}
"""

    response = groq.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0,
    )

    return response.choices[0].message.content


def create_sources(results):
    sources = []

    for result in results:
        payload = result.payload

        video_id = payload["video_id"]
        start_time = payload["start_time"]
        end_time = payload["end_time"]

        sources.append(
            {
                "video_id": video_id,
                "video_title": payload.get("video_title"),
                "start_time": start_time,
                "end_time": end_time,
                "timestamp": format_timestamp(start_time),
                "url": create_youtube_url(
                    video_id,
                    start_time,
                ),
                "score": result.score,
            }
        )

    return sources


if __name__ == "__main__":
    question = input("Ask a question: ")

    results = search(question)

    answer = generate_answer(
        question,
        results,
    )

    sources = create_sources(results)

    print("\nANSWER")
    print(answer)

    print("\nSOURCES")

    for source in sources:
        print(
            f'{source["timestamp"]} → '
            f'{source["url"]}'
        )