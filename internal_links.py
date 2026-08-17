import urllib.request
import urllib.error
import urllib.parse
import json
import re
import base64
from config import WP_URL, WP_USERNAME, WP_PASSWORD, WP_TIMEOUT

def get_wp_posts(search_query, max_results=5):
    """Cerca articoli su WordPress tramite REST API."""
    if not WP_URL or not WP_USERNAME or not WP_PASSWORD:
        return []

    try:
        query = urllib.parse.quote(search_query[:50])
        url = WP_URL + "/wp-json/wp/v2/posts?search=" + query + "&per_page=" + str(max_results) + "&status=publish"
        credentials = base64.b64encode((WP_USERNAME + ":" + WP_PASSWORD).encode()).decode()

        req = urllib.request.Request(url)
        req.add_header("Authorization", "Basic " + credentials)

        with urllib.request.urlopen(req, timeout=WP_TIMEOUT) as resp:
            posts = json.loads(resp.read())
            results = []
            for post in posts:
                results.append({
                    "title": post.get("title", {}).get("rendered", ""),
                    "url":   post.get("link", ""),
                    "slug":  post.get("slug", ""),
                })
            return results
    except Exception as e:
        print("  Avviso internal links WP: " + str(e))
        return []

def extract_keywords(text, max_kw=3):
    """Estrae parole chiave significative dal testo."""
    stopwords = {"il", "la", "le", "lo", "gli", "i", "un", "una", "uno",
                 "di", "da", "in", "con", "su", "per", "tra", "fra",
                 "the", "a", "an", "of", "in", "on", "for", "with",
                 "e", "o", "ma", "se", "che", "come", "questo", "questa"}
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    filtered = [w for w in words if w not in stopwords]
    # Prendi le parole piu' frequenti
    freq = {}
    for w in filtered:
        freq[w] = freq.get(w, 0) + 1
    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [w for w, _ in sorted_words[:max_kw]]

def find_internal_links(article_title, article_content, max_links=3):
    """
    Trova link interni pertinenti su WordPress.
    Restituisce lista di dict {title, url, anchor}.
    """
    if not WP_URL:
        return []

    links = []
    seen_urls = set()

    # Cerca per titolo articolo
    keywords = extract_keywords(article_title + " " + article_content[:500])

    for kw in keywords:
        if len(links) >= max_links:
            break
        posts = get_wp_posts(kw)
        for post in posts:
            if post["url"] not in seen_urls and post["url"] != "":
                seen_urls.add(post["url"])
                links.append({
                    "title":  post["title"],
                    "url":    post["url"],
                    "anchor": post["title"],
                })
                if len(links) >= max_links:
                    break

    if links:
        print("  Link interni trovati: " + str(len(links)))
    else:
        print("  Nessun link interno pertinente trovato")

    return links

def format_links_for_prompt(links):
    """Formatta i link per inserirli nel prompt di Claude."""
    if not links:
        return ""
    result = "\nLINK INTERNI DISPONIBILI (usa solo quelli pertinenti, stile 'leggi qui: [titolo]'):\n"
    for l in links:
        result += "- " + l["title"] + " → " + l["url"] + "\n"
    return result
