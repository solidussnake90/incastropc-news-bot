import feedparser
import datetime
from config import RSS_FEEDS

def fetch_all(hours_back=24):
    articles = []
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(hours=hours_back)

    for source_name, url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                published = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime.datetime(*entry.published_parsed[:6])
                elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                    published = datetime.datetime(*entry.updated_parsed[:6])

                if published and published < cutoff:
                    continue

                summary = ""
                if hasattr(entry, "summary"):
                    summary = entry.summary[:500]
                elif hasattr(entry, "content"):
                    summary = entry.content[0].value[:500]

                articles.append({
                    "source":    source_name,
                    "title":     entry.get("title", "").strip(),
                    "url":       entry.get("link", ""),
                    "summary":   summary,
                    "published": published,
                })

            print(f"  ✓ {source_name}: {len(feed.entries)} articoli trovati")

        except Exception as e:
            print(f"  ✗ {source_name}: errore — {e}")

    print(f"\nTotale articoli raccolti: {len(articles)}")
    return articles
