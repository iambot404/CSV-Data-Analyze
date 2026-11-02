import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the repository
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(BASE_DIR / ".env")

# Gemini Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest")
GEMINI_MODELS_RAW = os.getenv(
    "GEMINI_MODELS",
    "gemini-flash-lite-latest,gemini-3.1-flash-lite,gemini-3.8-flash,gemini-2.0-flash"
)
GEMINI_MODELS = [m.strip() for m in GEMINI_MODELS_RAW.split(",") if m.strip()]

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")

# App Security & Limits
JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-csv-analyzer-key-2026-9f8a7b6c5d4e3f2")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 72

MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB limit
ALLOWED_EXTENSIONS = {"csv", "tsv", "txt"}

# Server Settings
PORT = int(os.getenv("PORT", 5500))
DEBUG = os.getenv("FLASK_ENV") != "production"
