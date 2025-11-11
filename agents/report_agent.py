from typing import List, Dict, Any
import json
import datetime
from openai import OpenAI
from services.utils import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL


# -------------------- Helper: create OpenAI client --------------------
def _client():
    if not OPENAI_API_KEY:
        raise RuntimeError("Missing OPENAI_API_KEY")
    if OPENAI_BASE_URL:
        return OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
    return OpenAI(api_key=OPENAI_API_KEY)


# -------------------- Helper: safe JSON serialization --------------------
def safe_json(data):
    """
    Converts any non-serializable object (like Timestamp, datetime, numpy, etc.)
    into a JSON-safe string.
    """
    def default(o):
        if isinstance(o, (datetime.datetime, datetime.date)):
            return o.isoformat()
        try:
            # Handle pandas/numpy Timestamp or similar
            if hasattr(o, "isoformat"):
                return o.isoformat()
            return str(o)
        except Exception:
            return str(o)
    return json.dumps(data, indent=2, default=default)


# -------------------- Build prompt for the AI --------------------
def make_prompt(
    company: str,
    ticker: str,
    user_prompt: str,
    quote: dict,
    financials: dict,
    ratios: dict,
    news: List[dict],
) -> List[Dict[str, Any]]:
    """
    Builds the AI prompt with all context: company info, financial data, ratios, and recent news.
    """

    content = {
        "company": company,
        "ticker": ticker,
        "user_prompt": user_prompt,
        "quote": quote,
        "ratios": ratios,
        "financials_keys": [k for k in financials.keys()],
        "news": news,
    }

    system = (
        "You are a senior sell-side equity research analyst. "
        "Write in clear, structured sections with numbered or titled headings. "
        "Be analytical, evidence-based, and avoid exaggeration."
    )

    user = f"""Create a full equity research report with the following sections:
1) Investment Summary (key insights and drivers)
2) Company Overview (business model, segments, and strategy)
3) Industry & Competitive Landscape (Porter’s 5 forces or similar)
4) Recent Developments & News (summarize key headlines)
5) Financial Analysis (growth, profitability, efficiency ratios)
6) Valuation (DCF or relative multiples explanation)
7) Risks & Mitigants
8) Catalysts & Outlook
9) Final Recommendation (Buy/Hold/Sell with reasoning)

Guidelines:
- Use the provided data JSON faithfully.
- If data is missing, state assumptions clearly.
- Maintain a professional, concise tone.
- Include 1–2 tables or bullet lists where relevant.
- Provide a short disclaimer at the end.

JSON Context:
{safe_json(content)}
"""

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


# -------------------- Generate report using OpenAI --------------------
def generate_report(
    company: str,
    ticker: str,
    user_prompt: str,
    quote: dict,
    financials: dict,
    ratios: dict,
    news: List[dict],
) -> str:
    """
    Calls the OpenAI model to generate a structured equity research report.
    """
    messages = make_prompt(company, ticker, user_prompt, quote, financials, ratios, news)
    client = _client()

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0.4,
        )
        report = response.choices[0].message.content
        return report

    except Exception as e:
        return f"⚠️ Error generating report: {str(e)}"
