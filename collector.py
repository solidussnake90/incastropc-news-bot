import feedparser
import datetime
from config import RSS_FEEDS

def fetch_all(hours_back=12):
    """
    Scarica tutti i feed RSS e restituisce lista di articoli
    pubblicati nelle ultime `hours_back` ore.
    """
    articles = []
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(hours=hours_back)

    for source_name, url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            count = 0
            for entry in feed.entries:
                published = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime.datetime(*entry.published_parsed[:6])
                elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                    published = datetime.datetime(*entry.updated_parsed[:6])

                # Scarta articoli troppo vecchi
                if published and published < cutoff:
                    continue

                # Scarta articoli senza data (probabilmente vecchi)
                if not published:
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
                count += 1

            print("  " + source_name + ": " + str(count) + " articoli recenti trovati")

        except Exception as e:
            print("  ERRORE " + source_name + ": " + str(e))

    print("\nTotale articoli recenti (ultime 12h): " + str(len(articles)))
    return articles
