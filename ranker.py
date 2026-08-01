import datetime
from config import BOOST_KEYWORDS, PENALTY_KEYWORDS, TOP_N

def score_article(article):
    text = (article["title"] + " " + article["summary"]).lower()
    score = 50

    # Boost keyword — titolo vale triplo
    for kw in BOOST_KEYWORDS:
        if kw.lower() in text:
            if kw.lower() in article["title"].lower():
                score += 9
            else:
                score += 3

    # Penalità keyword
    for kw in PENALTY_KEYWORDS:
        if kw.lower() in text:
            score -= 15

    # Recency boost — più è recente più vale
    if article["published"]:
        age_hours = (datetime.datetime.utcnow() - article["published"]).total_seconds() / 3600
        if age_hours <= 3:
            score += 20   # Ultimi 3 ore: boost massimo
        elif age_hours <= 6:
            score += 10   # Ultime 6 ore: boost medio
        elif age_hours <= 12:
            score += 0    # Ultime 12 ore: neutro
        else:
            score -= 20   # Più vecchio: penalità

    # Boost per parole chiave di attualità nel titolo
    news_keywords = ["released", "announces", "update", "launches", "now", "new",
                     "rilascia", "annuncia", "aggiorna", "disponibile", "nuovo", "nuova"]
    for kw in news_keywords:
        if kw in article["title"].lower():
            score += 8

    return max(0, min(100, score))


def rank_articles(articles):
    for a in articles:
        a["score"] = score_article(a)

    ranked = sorted(articles, key=lambda x: x["score"], reverse=True)

    # Deduplicazione per titolo simile
    seen = set()
    deduped = []
    for a in ranked:
        key = " ".join(a["title"].lower().split()[:6])
        if key not in seen:
            seen.add(key)
            deduped.append(a)

    top = deduped[:TOP_N]
    print("Selezionati " + str(len(top)) + " articoli su " + str(len(articles)) + " totali")
    for a in top:
        print("  [" + str(a["score"]) + "] " + a["title"][:70])
    return top
