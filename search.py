from duckduckgo_search import DDGS
import datetime as dt

def news_headlines(query: str, max_results: int=5, days: int=60):
    q = f"{query} stock company news"
    since = dt.datetime.utcnow() - dt.timedelta(days=days)
    results = []
    with DDGS() as ddgs:
        for r in ddgs.news(q, max_results=max_results):
            # r keys: title, date, body, url, source, image
            results.append({
                "title": r.get("title"),
                "date": r.get("date"),
                "snippet": r.get("body"),
                "url": r.get("url"),
                "source": r.get("source"),
            })
    return results
