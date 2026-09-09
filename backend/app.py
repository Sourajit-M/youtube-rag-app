from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.config import TOP_K_DEFAULT
from backend.ingest import ingest_url
from backend.retrieval import get_indexed_videos
from backend.generate import generate_answer

app = FastAPI(
    title="YouTube RAG API",
    description="Timestamp-grounded Q&A over YouTube videos and playlists",
    version="1.0.0",
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request schemas
class IngestRequest(BaseModel):
    url: str
    force: bool = False


class QueryRequest(BaseModel):
    query: str


@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "YouTube RAG API is running"}


@app.get("/api/videos")
def list_videos():
    """Returns all unique indexed videos with their titles and chunk counts."""
    try:
        videos = get_indexed_videos()
        return {"videos": videos, "total": len(videos)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch indexed videos: {str(e)}")


@app.post("/api/ingest")
def ingest_endpoint(payload: IngestRequest):
    """
    Ingests a single YouTube video or a playlist from a URL.
    Extracts transcript, chunks, translates, embeds (dense + sparse), and upserts to Qdrant.
    """
    if not payload.url or not payload.url.strip():
        raise HTTPException(status_code=400, detail="A valid YouTube URL must be provided.")

    try:
        results = ingest_url(url=payload.url.strip(), force=payload.force)
        return {
            "status": "completed",
            "results": results,
            "total_processed": len(results),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@app.post("/api/query")
def query_endpoint(payload: QueryRequest):
    """
    Answers a question grounded in the indexed transcripts using Qdrant Hybrid Search + Groq.
    Returns the answer and timestamp citations.
    """
    if not payload.query or not payload.query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty.")

    try:
        response = generate_answer(query=payload.query.strip())
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)
