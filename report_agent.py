from typing import List, Dict, Any
import json
from openai import OpenAI
from services.utils import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL

def _client():
    if not OPENAI_API_KEY:
        raise RuntimeError("Missing OPENAI_API_KEY")
    if OPENAI_BASE_URL:
        return OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
    return OpenAI(api_key=OPENAI_API_KEY)

def make_prompt(company: str, ticker: str, user_prompt: str, quote: dict, financials: dict, ratios: dict, news: List[dict]) -> List[Dict[str, Any]]:
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
1) Investment Summary (1-2 paragraphs and bullet points with upside/downside drivers)
2) Company Overview (business model, segments, geographies)
3) Industry & Competitive Landscape (Porter 5 forces or similar)
4) Recent Developments & News (cite sources inline as [source])
5) Financial Analysis (growth, profitability, efficiency; reference provided ratios)
6) Valuation (explain method; provide ranges and key assumptions; note limitations)
7) Risks & Mitigants
8) Catalysts & Timeline
9) Conclusion (clear stance: Buy/Hold/Sell with rationale)

Guidelines:
- Use the provided JSON context faithfully.
- If any data is missing, state assumptions explicitly.
- Keep tone professional; avoid financial advice disclaimers beyond one brief note.
- Keep jargon minimal; define terms briefly if uncommon.
- Where relevant, include 1-2 short tables in Markdown.

JSON Context:
{json.dumps(content, indent=2)}
"""
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]

def generate_report(company: str, ticker: str, user_prompt: str, quote: dict, financials: dict, ratios: dict, news: List[dict]) -> str:
    messages = make_prompt(company, ticker, user_prompt, quote, financials, ratios, news)
    client = _client()
    # Use Chat Completions for broad compatibility
    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        temperature=0.4,
    )
    return resp.choices[0].message.content
