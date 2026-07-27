import datetime
from config import BOOST_KEYWORDS, PENALTY_KEYWORDS, TOP_N

def score_article(article):
    text = (article["title"] + " " + article["summary"]).lower()
    score = 50

    for kw in BOOST_KEYWORDS:
        if kw.lower() in text:
            if kw.lower() in article["title"].lower():
                score += 6
            else:
                score += 3

    for kw in PENALTY_KEYWORDS:
        if kw.lower() in text:
            score -= 8

    if article["published"]:
        age_hours = (datetime.datetime.utcnow() - article["published"]).total_seconds() / 3600
        score -= int(age_hours / 2)

    return max(0, min(100, score))


def rank_articles(articles):
    for a in articles:
        a["score"] = score_article(a)

    ranked = sorted(articles, key=lambda x: x["score"], reverse=True)

    seen = set()
    deduped = []
    for a in ranked:
        key = " ".join(a["title"].lower().split()[:6])
        if key not in seen:
            seen.add(key)
            deduped.append(a)

    top = deduped[:TOP_N]
    print(f"Selezionati {len(top)} articoli su {len(articles)} totali")
    return top
