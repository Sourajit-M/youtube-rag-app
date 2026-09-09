import groq
from backend.config import GROQ_API_KEY, GROQ_MODEL, TOP_K_DEFAULT
from backend.retrieval import hybrid_search

client = groq.Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """You are a helpful assistant that answers questions using provided YouTube video transcript excerpts.
Rules:
1. Answer using ONLY the facts directly mentioned in the context excerpts.
2. If the context does not contain enough information to answer, state: "This topic is not covered in the ingested video(s)."
3. Format your response cleanly in Markdown.
"""

def generate_answer(query: str) -> dict:
    """Retrieves relevant transcript chunks from all stored videos in the DB and generates a grounded answer."""
    # 1. Hybrid search (dense + BM25 via Qdrant Cloud) across all stored videos
    hits = hybrid_search(query=query)
    if not hits:
        return {
            "query": query,
            "answer": "This topic is not covered in the ingested video(s).",
            "citations": [],
        }

    # 2. Build context string from retrieved chunks
    context_text = "\n\n".join(
        f"[{i+1}] Video: {h['video_title']} @ {h['timestamp_formatted']}\n{h['text']}"
        for i, h in enumerate(hits)
    )

    # 3. Call Groq LLM
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Context:\n{context_text}\n\nQuestion: {query}\n\nAnswer:",
            },
        ],
        temperature=0.2,
    )

    # 4. Return answer, formatted citations, and full context excerpts
    return {
        "query": query,
        "answer": response.choices[0].message.content.strip(),
        "context_excerpts": [h["text"] for h in hits],
        "citations": [
            {
                "video_id": h["video_id"],
                "video_title": h["video_title"],
                "start_time": h["start_time"],
                "timestamp_formatted": h["timestamp_formatted"],
                "youtube_url": h["youtube_url"],
                "context": h["text"],
                "snippet": h["text"][:150] + ("..." if len(h["text"]) > 150 else ""),
            }
            for h in hits
        ],
    }


if __name__ == "__main__":
    test_query = "What is method overriding and how it is performed with an example."
    result = generate_answer(test_query)
    print("\n=== Answer ===")
    print(result["answer"])
    print("\n=== Citations ===")
    for c in result["citations"]:
        print(f"- [{c['timestamp_formatted']}] {c['video_title']}: {c['youtube_url']}")