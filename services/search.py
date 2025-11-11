import os
import requests
import streamlit as st
from duckduckgo_search import DDGS

# Optional NewsData.io API key (add to Streamlit Secrets if you want)
NEWS_API_KEY = os.getenv("NEWSDATA_API_KEY", None)

# ----------------------------------------------------------------------
# 📰 Fetch Latest News Headlines
# ----------------------------------------------------------------------

@st.cache_data(ttl=3600)
def news_headlines(company: str, max_results: int = 5):
    """
    Fetches recent news headlines about a company.
    - Uses NewsData.io if API key is provided.
    - Falls back to DuckDuckGo Search if no API key.
    - Returns placeholder if rate-limited or failed.
    """
    try:
        # ✅ Option 1: Use NewsData.io (if key available)
        if NEWS_API_KEY:
            url = f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&q={company}&language=en"
            res = requests.get(url)
            data = res.json()

            if "results" in data and data["results"]:
                headlines = [
                    {
                        "title": n.get("title", "Untitled"),
                        "href": n.get("link", ""),
                    }
                    for n in data["results"][:max_results]
                ]
                return headlines

        # ✅ Option 2: Fallback to DuckDuckGo Search
        with DDGS() as ddgs:
            results = list(ddgs.text(f"{company} stock company news", max_results=max_results))

        if results:
            headlines = [
                {"title": r.get("title", ""), "href": r.get("href", "")}
                for r in results
            ]
            return headlines

        # ✅ If no results
        return [
            {"title": f"No news found for {company}.", "href": ""},
        ]

    except Exception as e:
        # ✅ Graceful fallback when rate-limited or blocked
        return [
            {
                "title": f"{company} — Unable to fetch live news (Rate limit or connection issue).",
                "href": "",
            },
            {
                "title": "You can manually check the latest company updates on financial portals like Moneycontrol, Reuters, or Yahoo Finance.",
                "href": "",
            },
        ]
