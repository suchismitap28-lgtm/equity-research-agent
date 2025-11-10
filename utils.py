import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", None)
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

def mask(s: str, keep=4) -> str:
    if not s:
        return ""
    return s[:keep] + "..." + s[-keep:] if len(s) > keep*2 else "***"
