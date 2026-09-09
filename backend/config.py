import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

# Qdrant Cloud settings
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "youtube_rag_videos")

# Groq LLM settings
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

# Embedding & Search settings
DENSE_MODEL_NAME = "all-MiniLM-L6-v2"
DENSE_VECTOR_SIZE = 384
SPARSE_MODEL_NAME = "Qdrant/bm25"

# Chunking & Retrieval parameters
CHUNK_WINDOW_SECONDS = 45
CHUNK_OVERLAP_SECONDS = 10
TOP_K_DEFAULT = 6
