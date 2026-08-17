import sys
import os
import re
import json
import base64
import urllib.request
import urllib.error
from collector import fetch_all
from ranker    import rank_articles
from writer    import generate_digest
from mailer    import send_digest, parse_articles, parse_consigliato

WP_URL      = os.environ.get("WP_URL", "").rstrip("/")
WP_USERNAME = os.environ.get("WP_USERNAME", "")
WP_PASSWORD = os.environ.get("WP_PASSWORD", "")

def wp_publish(title, content, slug, keyphrase, metadesc):
    """Pubblica un articolo su WordPress come PUBBLICATO (non bozza)."""
    if not WP_URL or not WP_USERNAME or not WP_PASSWORD:
        print("  Credenziali WordPress mancanti, salto pubblicazione")
        return None

    credentials = base64.b64encode((WP_USERNAME + ":" + WP_PASSWORD).encode()).decode()
    api_url = WP_URL + "/wp-json/wp/v2/posts"

    post_data = json.dumps({
        "title":   title,
        "content": content,
        "status":  "publish",
        "slug":    slug,
        "meta": {
            "_yoast_wpseo_focuskw": keyphrase,
            "_yoast_wpseo_metadesc": metadesc,
        }
    }).encode("utf-8")

    req = urllib.request.Request(api_url, data=post_data, method="POST")
    req.add_header("Authorization", "Basic " + credentials)
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            post_id  = result.get("id", "?")
            post_url = result.get("link", "")
            print("  Articolo pubblicato: " + post_url)
            return post_url
    except urllib.error.HTTPError as e:
        error = e.read().decode("utf-8")
        print("  Errore WordPress HTTP " + str(e.code) + ": " + error[:300])
    except Exception as e:
        print("  Errore WordPress: " + str(e))
    return None

def extract_article_data(block):
    """Estrae titolo, contenuto e dati SEO da un blocco articolo."""
    title = slug = keyphrase = metadesc = ""
    clean_lines = []

    for line in block.split("\n"):
        if line.startswith("YOAST_KEYPHRASE:"):
            keyphrase = line.replace("YOAST_KEYPHRASE:", "").strip()
        elif line.startswith("YOAST_METADESC:"):
            metadesc = line.replace("YOAST_METADESC:", "").strip()
        elif line.startswith("YOAST_SLUG:"):
            slug = line.replace("YOAST_SLUG:", "").strip()
        elif line.startswith("IMAGE_COVER:") or line.startswith("IMAGE_BODY:"):
            continue
        else:
            clean_lines.append(line)

    content = "\n".join(clean_lines).strip()
    match = re.search(r"<h1>(.*?)</h1>", content)
    if match:
        title = match.group(1).strip()

    return title, content, slug, keyphrase, metadesc

def run():
    print("=" * 50)
    print("  IncastroPC News Bot — avvio")
    print("=" * 50)

    print("\n[1/4] Raccolta articoli RSS...")
    articles = fetch_all(hours_back=12)

    if not articles:
        print("Nessun articolo trovato. Uscita.")
        sys.exit(0)

    print("\n[2/4] Ranking per rilevanza...")
    top_articles = rank_articles(articles)

    print("\n[3/4] Generazione articoli con Claude...")
    digest_html = generate_digest(top_articles)

    print("\n[4/4] Pubblicazione articolo consigliato su WordPress...")
    article_blocks = parse_articles(digest_html)
    consigliato_text = parse_consigliato(digest_html)

    published_url = None
    published_title = None

    # Trova il numero dell'articolo consigliato
    try:
        lines = consigliato_text.strip().split("\n")
        numero = int(lines[0].strip()) - 1
        if 0 <= numero < len(article_blocks):
            block = article_blocks[numero]
            title, content, slug, keyphrase, metadesc = extract_article_data(block)
            print("  Pubblico: " + title)
            published_url = wp_publish(title, content, slug, keyphrase, metadesc)
            published_title = title
    except Exception as e:
        print("  Errore selezione articolo consigliato: " + str(e))

    print("\n[5/5] Invio email...")
    wp_info = [(published_title, published_url)] if published_url else []
    send_digest(digest_html, wp_info)

    print("\n✓ Bot completato con successo!")

if __name__ == "__main__":
    run()
