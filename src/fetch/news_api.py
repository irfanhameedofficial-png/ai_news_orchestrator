# src/fetch/news_api.py
import requests

# Directly put your key here for testing only
NEWSAPI_KEY = "aedd6ad241f240979c902501a73f70eb"

if not NEWSAPI_KEY:
    raise RuntimeError("NEWSAPI_KEY is not set!")

def fetch_news(query: str, limit: int = 6):
    """
    Fetch articles from newsapi.org. Returns list of dicts:
    { headline, summary, url, published, source }
    """
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "pageSize": limit,
        "language": "en",
        "sortBy": "relevancy",
        "apiKey": NEWSAPI_KEY,
    }

    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    payload = resp.json()

    articles = []
    for a in payload.get("articles", []):
        articles.append({
            "headline": a.get("title") or "",
            "summary": a.get("description") or a.get("content") or "",
            "url": a.get("url") or "",
            "published": a.get("publishedAt") or "",
            "source": (a.get("source") or {}).get("name", "")
        })

    return articles
