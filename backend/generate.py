import sys
from typing import List, Dict, Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from backend.config import GROQ_API_KEY, GROQ_MODEL
from backend.retrieval import hybrid_search

# 1. Initialize LangChain Groq model
llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model_name=GROQ_MODEL,
    temperature=0.2,
)

# 2. Define the Prompt Template (supports optional multi-turn conversation)
prompt_template = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a helpful assistant that answers questions using provided YouTube video transcript excerpts.\n"
        "Rules:\n"
        "1. Answer using ONLY the facts directly mentioned in the context excerpts.\n"
        "2. If the context does not contain enough information to answer, state: 'This topic is not covered in the ingested video(s).'\n"
        "3. Format your response cleanly in Markdown.\n\n"
        "Context Excerpts:\n{context}",
    ),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}"),
])

# 3. Create the simple LCEL chain
rag_chain = prompt_template | llm


def _format_chat_history(raw_history: Optional[List[Dict[str, str]]] = None):
    """Converts a list of {'role': 'user'|'assistant', 'content': '...'} into LangChain messages."""
    messages = []
    if not raw_history:
        return messages
    for msg in raw_history:
        if msg.get("role") == "user":
            messages.append(HumanMessage(content=msg.get("content", "")))
        elif msg.get("role") == "assistant":
            messages.append(AIMessage(content=msg.get("content", "")))
    return messages


def generate_answer(query: str, chat_history: Optional[List[Dict[str, str]]] = None) -> dict:
    """
    1. Runs native Qdrant Hybrid Search from retrieval.py
    2. Passes context & optional chat history through LangChain ChatGroq
    3. Returns grounded answer with exact timestamp citations
    """
    # 1. Native Qdrant Hybrid Search (Dense + BM25 via Qdrant Cloud RRF)
    hits = hybrid_search(query=query)
    if not hits:
        return {
            "query": query,
            "answer": "This topic is not covered in the ingested video(s).",
            "citations": [],
            "context_excerpts": [],
        }

    # 2. Build readable context from retrieved chunks
    context_text = "\n\n".join(
        f"[{i+1}] Video: {h['video_title']} @ {h['timestamp_formatted']}\n{h['text']}"
        for i, h in enumerate(hits)
    )

    # 3. Invoke LangChain Chain
    history_messages = _format_chat_history(chat_history)
    response = rag_chain.invoke({
        "context": context_text,
        "chat_history": history_messages,
        "question": query,
    })

    # 4. Format citations and return
    citations = [
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
    ]

    return {
        "query": query,
        "answer": response.content.strip(),
        "context_excerpts": [h["text"] for h in hits],
        "citations": citations,
    }


if __name__ == "__main__":
    test_query = "What is polymorphism and inheritance?"
    result = generate_answer(test_query)
    print("\n=== Answer ===")
    print(result["answer"])
    print("\n=== Citations ===")
    for c in result["citations"]:
        print(f"- [{c['timestamp_formatted']}] {c['video_title']}: {c['youtube_url']}")