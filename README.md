# YouTube RAG — Timestamp-Grounded Q&A over Videos & Playlists

A production-grade Retrieval-Augmented Generation (RAG) application that ingests single YouTube videos or entire playlists across multiple languages and answers questions in English. Every answer is strictly grounded in the video transcripts and includes **clickable timestamp citations** that seek an embedded YouTube player directly to the exact second where the concept is explained.

This project was built from scratch with **$0 infrastructure cost**, leveraging free tiers across vector storage, inference, and embeddings.

---

## Key Highlights

- **100% Free-Tier Stack**: Built with Qdrant Cloud Free Tier (1GB managed cluster), Groq Free Tier (`openai/gpt-oss-120b`), and local sentence-transformers — zero hosting or inference cost.
- **Qdrant Cloud Native Hybrid Search**: Fuses dense semantic vector embeddings (`all-MiniLM-L6-v2`) with sparse keyword vectors (`fastembed Qdrant/bm25`) using server-side **Reciprocal Rank Fusion (RRF)** directly inside Qdrant Cloud.
- **Multi-Language Ingestion & Universal Translation**: Videos in Hindi, French, Spanish, etc., are automatically detected and batch-translated into English pre-indexing using `deep-translator`.
- **Timestamp-Anchored Chunking**: Transcript segments are windowed into semantic blocks (~75s / 150–250 tokens) while anchoring the start timestamp strictly to the first subtitle to eliminate timestamp drift.
- **Minimalist Off-White UI**: Built with React + Vite using an editorial off-white aesthetic (`#f8f9fa` / `#ffffff`), clean Plus Jakarta Sans typography, a slide-over Knowledge Base Drawer, and an embedded YouTube player that automatically seeks on citation clicks.
- **Automated RAGAS Evaluation Harness**: Standalone offline benchmark script using Groq as an LLM judge to track **Faithfulness**, **Answer Relevancy**, **Context Precision**, and **Context Recall** over iterations.

---

## Architecture Diagram

```
                               ┌─────────────────────────────┐
                               │       React Frontend        │
                               │  (Vite + Plus Jakarta Sans) │
                               └──────────────┬──────────────┘
                                              │ HTTP / JSON
                                              ▼
                               ┌─────────────────────────────┐
                               │       FastAPI Backend       │
                               │      (backend/app.py)       │
                               └──────┬───────────────┬──────┘
                                      │               │
                  [ Ingestion Pipeline ]             [ Hybrid Retrieval & Generation ]
                                      │               │
              yt-dlp (metadata & playlists)          User Query (English)
                                      │               ├── Dense: all-MiniLM-L6-v2 (top-k)
        youtube-transcript-api (timestamps)          ├── Sparse: fastembed Qdrant/bm25 (top-k)
                                      │               └── Fusion: Server-Side RRF in Qdrant Cloud
              deep-translator (Any -> EN)                     │
                                      │               Retrieved Context + System Prompt
            Segment-aware Chunking (~75s)                     │
                                      │               Groq LLM (openai/gpt-oss-120b)
        Dense (MiniLM) + Sparse (BM25) Embed                  │
                                      ▼                       ▼
                         Qdrant Cloud Free Tier        Grounded Answer + Clickable Timestamps
```

---

## Project Structure

```
youtube-rag-app/
├── backend/
│   ├── app.py              # FastAPI server (/api/ingest, /api/query, /api/videos, /api/health)
│   ├── config.py           # Centralized configuration & environment constants
│   ├── ingest.py           # URL resolution, multi-language translation, chunking, & dual indexing
│   ├── retrieval.py        # Dense + BM25 sparse search with server-side RRF in Qdrant Cloud
│   ├── generate.py         # Grounded response generation via Groq (openai/gpt-oss-120b)
│   ├── evaluate.py         # Standalone RAGAS evaluation harness (faithfulness & relevance judge)
│   └── golden_dataset.json # Curated 15-question benchmark dataset across mixed videos
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # Lightweight root layout coordinator
│   │   ├── index.css       # Off-white design system & markdown typography
│   │   └── components/
│   │       ├── Header.jsx       # Branding & Library drawer trigger
│   │       ├── IngestBar.jsx    # URL input, ingest button, & compact summary bar
│   │       ├── VideoLibrary.jsx # Slide-over drawer with video search & filtering
│   │       ├── ChatArea.jsx     # Message stream, suggestions, & question input
│   │       ├── CitationBadge.jsx# Clickable timestamp pill badges ([▶ 01:28:35])
│   │       └── VideoPlayer.jsx  # Embedded 16:9 YouTube player with timestamp seek
│   ├── package.json
│   └── vite.config.js      # Vite config with backend proxy to :8000
├── pyproject.toml          # UV project dependencies
├── .env.example            # Template for environment variables
├── eval_results.csv        # Automated log of evaluation benchmark runs
└── README.md
```

---

## Quickstart Guide

### 1. Prerequisites
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- Node.js 18+ and npm

### 2. Environment Setup
Clone the repository and copy the environment template:
```bash
cp .env.example .env
```

Configure your free API keys in `.env`:
```ini
QDRANT_URL=https://your-cluster-id.region.gcp.cloud.qdrant.io:6333
QDRANT_API_KEY=your_qdrant_api_key
GROQ_API_KEY=gsk_your_groq_api_key
```

### 3. Backend Setup
Install dependencies with `uv`:
```bash
uv sync
```

Start the FastAPI server:
```bash
uv run python -m uvicorn backend.app:app --reload --port 8000
```
Interactive Swagger documentation is available at `http://localhost:8000/docs`.

### 4. Frontend Setup
In a separate terminal, start the React dev server:
```bash
cd frontend
npm install
npm run dev
```
Open **`http://localhost:5173`** in your browser.

---

## RAGAS Evaluation Benchmark

The system includes an automated evaluation harness in `backend/evaluate.py` that assesses outputs across the **4 core RAGAS metrics**:

1. **Faithfulness**: Verifies whether all factual claims in the generated answer are grounded in the retrieved transcripts.
2. **Answer Relevancy**: Assesses how directly the answer addresses the user prompt.
3. **Context Precision**: Measures the ratio of retrieved chunks that are actually relevant to the question.
4. **Context Recall**: Verifies whether the retrieved context contains the necessary information specified in the ground truth.

To run the offline benchmark:
```bash
uv run python -m backend.evaluate
```

Results are automatically appended to `eval_results.csv` with a timestamp to track retrieval performance across iterations:

| Run Iteration | Faithfulness | Answer Relevancy | Context Precision | Context Recall | Overall RAGAS |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **v1: 45s Chunks (Truncated Context)** | 0.617 | 1.000 | 0.403 | 0.420 | 0.610 |
| **v2: 75s Chunks + Full Context (Mixed Hindi/English)** | **0.947** | **1.000** | **0.629** | **0.640** | **0.804** |

---

## Technical Design Decisions & Interview Talking Points

- **Why Reciprocal Rank Fusion (RRF)?**: Score normalization between dense cosine distance and sparse BM25 scores is fragile and requires tuning an arbitrary $\alpha$ weight. RRF uses pure rank position:
  $$RRF(d) = \sum_{m \in \{\text{dense}, \text{sparse}\}} \frac{1}{60 + \text{rank}_m(d)}$$
  which provides robust, scale-invariant hybrid retrieval.
- **Server-Side Fusion in Qdrant Cloud**: Instead of maintaining a separate BM25 database locally on disk (which creates state and sync issues on ephemeral cloud hosts), we use FastEmbed's `Qdrant/bm25` sparse vectors stored alongside dense vectors directly in Qdrant Cloud.
- **Hallucination Guardrails**: Prompts strictly instruct the model to state *"This topic is not covered in the ingested video(s)"* when context is insufficient, verified by our negative out-of-domain benchmark questions scoring 1.0.

---

## License
MIT License
