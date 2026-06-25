"""
Central configuration module for Smart Admin Assistant.
All settings are loaded from .env and exposed as constants.
Usage: from app.config import GROQ_API_KEY, CONFIDENCE_THRESHOLD, ...
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ─── Load .env ───────────────────────────────────────────────
load_dotenv()

# ─── Paths ───────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_WEB_DIR = DATA_DIR / "raw_web"
MANUAL_FAQS_DIR = DATA_DIR / "manual_faqs"
STRUCTURED_DIR = DATA_DIR / "structured"
LOGS_DIR = PROJECT_ROOT / "logs"
PROMPTS_DIR = Path(__file__).parent / "prompts"
VECTOR_STORE_DIR = Path(
    os.getenv("CHROMA_PERSIST_DIR", str(PROJECT_ROOT / "vector_store" / "chroma_db"))
)

# ─── Groq API (Primary LLM) ─────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-8b-8192")

# ─── Embedding Model ────────────────────────────────────────
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-base")

# ─── Supabase (Optional) ────────────────────────────────────
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# ─── RAG Settings ───────────────────────────────────────────
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.38"))
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "5"))

# ─── App Settings ───────────────────────────────────────────
GRADIO_PORT = int(os.getenv("GRADIO_PORT", "7860"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ─── Prompt Templates ───────────────────────────────────────
SYSTEM_PROMPT_AR_PATH = PROMPTS_DIR / "system_ar.txt"
SYSTEM_PROMPT_EN_PATH = PROMPTS_DIR / "system_en.txt"
FALLBACK_PROMPT_AR_PATH = PROMPTS_DIR / "fallback_ar.txt"
FALLBACK_PROMPT_EN_PATH = PROMPTS_DIR / "fallback_en.txt"

# ─── Log Files ──────────────────────────────────────────────
GAP_LOG_PATH = LOGS_DIR / "query_gaps.jsonl"
FEEDBACK_LOG_PATH = LOGS_DIR / "feedback.jsonl"
APP_LOG_PATH = LOGS_DIR / "app.log"
