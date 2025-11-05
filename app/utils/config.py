from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

_env_path = Path(__file__).resolve().parents[2] / ".env"
if _env_path.exists():
    load_dotenv(_env_path)

PORT = int(os.getenv("PORT", "8000"))
HOST = os.getenv("HOST", "0.0.0.0")
WEB_ORIGIN = os.getenv("WEB_ORIGIN", "http://localhost:5173")

SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", "meetings@example.com")

VECTOR_INDEX_PATH = os.getenv("VECTOR_INDEX_PATH", ".vector_index")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./meeting_helper.db")

