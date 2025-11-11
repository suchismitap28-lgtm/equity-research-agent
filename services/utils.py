import os
from dotenv import load_dotenv

# Load environment variables from .env (for local runs)
load_dotenv()

# ----------------------------------------------------------------------
# 🧠 Universal LLM Configuration
# Works with OpenAI, Groq, Together AI, DeepInfra, etc.
# ----------------------------------------------------------------------

# The same variable names are used for all OpenAI-compatible APIs.
# Just update these in your Streamlit secrets or .env file.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# ----------------------------------------------------------------------
# 🧩 Diagnostic Helper
# ----------------------------------------------------------------------

def show_current_llm_config():
    """Return the current model and base URL for quick debugging."""
    if not OPENAI_API_KEY:
        return "⚠️ No API key detected. Please set OPENAI_API_KEY."
    if "groq.com" in (OPENAI_BASE_URL or ""):
        provider = "Groq (Llama 3)"
    elif "together.xyz" in (OPENAI_BASE_URL or ""):
        provider = "Together AI"
    elif "openrouter.ai" in (OPENAI_BASE_URL or ""):
        provider = "OpenRouter"
    elif "openai.com" in (OPENAI_BASE_URL or ""):
        provider = "OpenAI"
    else:
        provider = "Custom Provider"
    return f"✅ Using {provider} | Model: {OPENAI_MODEL}"

# ----------------------------------------------------------------------
# 🪄 Key Masking Utility (for UI display)
# ----------------------------------------------------------------------

def mask(s: str, keep=4) -> str:
    """Mask API keys so they can be safely shown in Streamlit UI."""
    if not s:
        return ""
    return s[:keep] + "..." + s[-keep:] if len(s) > keep * 2 else "***"

