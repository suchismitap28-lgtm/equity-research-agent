import json
import openai
import os
from services.utils import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL

# Configure client
client = openai.OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL
)

# ----------------------------------------------------------------------
# 🧠 Helper: Truncate Large Inputs to Avoid Context Errors
# ----------------------------------------------------------------------
def truncate_text(text, max_chars=800):
    if not text:
        return ""
    return text[:max_chars] + "..." if len(text) > max_chars else text


def summarize_large_data(data_dict, max_items=10):
    """
    Converts large dictionaries or lists into shorter summaries
    to fit context length safely.
    """
    if isinstance(data_dict, dict):
        short_data = {}
        for i, (k, v) in enumerate(data_dict.items()):
            if i >= max_items:
                break
            short_data[k] = truncate_text(str(v))
        return short_data

    elif isinstance(data_dict, list):
        return [truncate_text(str(item)) for item in data_dict[:max_items]]

    return truncate_text(str(data_dict))


# ----------------------------------------------------------------------
# 🧾 Main Report Generation Function
# ----------------------------------------------------------------------
def generate_report(company, ticker, user_prompt, quote, financials, ratios, news):
    """
    Generates a summarized equity research report using AI.
    Handles large input data safely by truncating and summarizing.
    """

    # ✅ Step 1: Summarize or trim all inputs
    company = truncate_text(company or ticker, 100)
    user_prompt = truncate_text(user_prompt, 600)

    quote_summary = summarize_large_data(quote, max_items=10)
    ratios_summary = summarize_large_data(ratios, max_items=10)
    financials_summary = summarize_large_data(financials, max_items=5)
    news_summary = summarize_large_data(news, max_items=5)

    # ✅ Step 2: Build a compact, structured prompt
    system_prompt = (
        "You are a professional equity research analyst. "
        "Your goal is to write a concise yet insightful equity research report "
        "based on the provided company data, financial summary, and recent news. "
        "Focus on key metrics, valuation insights, competitive position, and investment outlook. "
        "Avoid unnecessary repetition. Use bullet points or short paragraphs."
    )

    user_message = f"""
    Company: {company}
    Ticker: {ticker}

    --- Key Financial Highlights ---
    {json.dumps(financials_summary, indent=2)}

    --- Valuation Ratios ---
    {json.dumps(ratios_summary, indent=2)}

    --- Market Summary ---
    {json.dumps(quote_summary, indent=2)}

    --- Recent News Headlines ---
    {json.dumps(news_summary, indent=2)}

    --- Custom Analyst Instructions ---
    {user_prompt}

    Generate a well-structured equity research report including:
    1. Executive Summary
    2. Business Overview
    3. Financial Analysis
    4. Valuation & Outlook
    5. Key Risks & Opportunities
    6. Investment Recommendation
    """

    # ✅ Step 3: Make API call safely
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=1500,  # limits the output size
            temperature=0.7
        )

        report = response.choices[0].message.content.strip()
        return report

    except Exception as e:
        return f"⚠️ Error generating report: {e}"
