import os
import json
import re
import urllib.request
import urllib.error
import base64
from config import WP_URL, WP_USERNAME, WP_PASSWORD, WP_TIMEOUT

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "data", "published.json")

def load_history():
    """Carica lo storico degli articoli pubblicati."""
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(history):
    """Salva lo storico."""
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history[-500:], f, ensure_ascii=False, indent=2)  # max 500 entries

def normalize_title(title):
    """Normalizza il titolo per confronto."""
    title = title.lower().strip()
    title = re.sub(r'[^\w\s]', '', title)
    title = re.sub(r'\s+', ' ', title)
    return title

def title_similarity(t1, t2):
    """Calcola similarita' tra due titoli (0-1)."""
    w1 = set(normalize_title(t1).split())
    w2 = set(normalize_title(t2).split())
    if not w1 or not w2:
        return 0
    intersection = w1 & w2
    union = w1 | w2
    return len(intersection) / len(union)

def check_wp_duplicates(title, max_results=10):
    """Cerca articoli simili su WordPress tramite REST API."""
    if not WP_URL or not WP_USERNAME or not WP_PASSWORD:
        return False

    try:
        # Prende le prime parole chiave del titolo
        keywords = " ".join(normalize_title(title).split()[:4])
        url = WP_URL + "/wp-json/wp/v2/posts?search=" + urllib.request.quote(keywords) + "&per_page=" + str(max_results)
        credentials = base64.b64encode((WP_USERNAME + ":" + WP_PASSWORD).encode()).decode()

        req = urllib.request.Request(url)
        req.add_header("Authorization", "Basic " + credentials)
        req.add_header("User-Agent", "Mozilla/5.0 IncastroPC-Bot/3.0")

        with urllib.request.urlopen(req, timeout=WP_TIMEOUT) as resp:
            posts = json.loads(resp.read())
            for post in posts:
                wp_title = post.get("title", {}).get("rendered", "")
                similarity = title_similarity(title, wp_title)
                if similarity > 0.6:
                    print("  Duplicato trovato su WP: " + wp_title[:60])
                    return True
    except Exception as e:
        print("  Avviso check WP duplicati: " + str(e))

    return False

def is_duplicate(article):
    """
    Controlla se un articolo e' un duplicato.
    Controlla: storico locale + WordPress.
    """
    title = article.get("title", "")
    url   = article.get("url", "")

    # 1. Controlla storico locale
    history = load_history()
    for entry in history:
        # Stesso URL
        if entry.get("url") == url:
            print("  Duplicato URL locale: " + title[:60])
            return True
        # Titolo molto simile
        if title_similarity(title, entry.get("title", "")) > 0.7:
            print("  Duplicato titolo locale: " + title[:60])
            return True

    # 2. Controlla WordPress
    if check_wp_duplicates(title):
        return True

    return False

def add_to_history(article, wp_url=""):
    """Aggiunge un articolo allo storico dopo la pubblicazione."""
    history = load_history()
    history.append({
        "title":      article.get("title", ""),
        "url":        article.get("url", ""),
        "wp_url":     wp_url,
        "published":  str(article.get("published", "")),
        "source":     article.get("source", ""),
    })
    save_history(history)
