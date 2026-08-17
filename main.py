import sys
import os
import re
import json
import base64
import urllib.request
import urllib.error

from collector        import fetch_all
from ranker           import rank_articles
from writer           import generate_digest
from mailer           import send_digest, parse_articles, parse_consigliato
from duplicate_checker import is_duplicate, add_to_history
from internal_links   import find_internal_links
from image_generator  import generate_article_images

from config import (
    WP_URL, WP_USERNAME, WP_PASSWORD, WP_STATUS, WP_TIMEOUT,
    HOURS_BACK, MIN_SCORE, IN_ARTICLE_IMAGES
)

# ─── Log riepilogo ciclo ──────────────────────────────────
stats = {
    "fonti_controllate": 0,
    "news_trovate":      0,
    "news_pertinenti":   0,
    "duplicati":         0,
    "news_generate":     0,
    "pubblicate":        0,
    "errori":            0,
}

def wp_publish(title, content, slug, keyphrase, metadesc, tags, featured_media_id=None):
    """Pubblica su WordPress con timeout e status configurabile."""
    if not WP_URL or not WP_USERNAME or not WP_PASSWORD:
        print("  Credenziali WordPress mancanti")
        return None

    credentials = base64.b64encode((WP_USERNAME + ":" + WP_PASSWORD).encode()).decode()
    api_url = WP_URL + "/wp-json/wp/v2/posts"

    post_data = {
        "title":   title,
        "content": content,
        "status":  WP_STATUS,
        "slug":    slug,
        "meta": {
            "_yoast_wpseo_focuskw":  keyphrase,
            "_yoast_wpseo_metadesc": metadesc,
        }
    }

    if featured_media_id:
        post_data["featured_media"] = featured_media_id

    payload = json.dumps(post_data).encode("utf-8")
    req = urllib.request.Request(api_url, data=payload, method="POST")
    req.add_header("Authorization", "Basic " + credentials)
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=WP_TIMEOUT) as resp:
            result = json.loads(resp.read())
            post_url = result.get("link", "")
            post_id  = result.get("id", "?")
            print("  Pubblicato [" + WP_STATUS + "]: " + post_url)
            return post_url
    except urllib.error.HTTPError as e:
        error = e.read().decode("utf-8")[:300]
        print("  Errore WordPress HTTP " + str(e.code) + ": " + error)
        stats["errori"] += 1
    except Exception as e:
        print("  Errore WordPress: " + str(e))
        stats["errori"] += 1
    return None

def extract_article_data(block):
    """Estrae tutti i dati da un blocco articolo."""
    title = slug = keyphrase = metadesc = ""
    tags = []
    cover_prompt = ""
    body_prompts = []
    social_caption = ""
    clean_lines = []

    for line in block.split("\n"):
        if line.startswith("YOAST_KEYPHRASE:"):
            keyphrase = line.replace("YOAST_KEYPHRASE:", "").strip()
        elif line.startswith("YOAST_METADESC:"):
            metadesc = line.replace("YOAST_METADESC:", "").strip()
        elif line.startswith("YOAST_SLUG:"):
            slug = line.replace("YOAST_SLUG:", "").strip()
        elif line.startswith("YOAST_TAGS:"):
            tags_str = line.replace("YOAST_TAGS:", "").strip()
            tags = [t.strip() for t in tags_str.split(",") if t.strip()]
        elif line.startswith("IMAGE_COVER:"):
            cover_prompt = line.replace("IMAGE_COVER:", "").strip()
        elif line.startswith("IMAGE_BODY_1:"):
            body_prompts.append(line.replace("IMAGE_BODY_1:", "").strip())
        elif line.startswith("IMAGE_BODY_2:"):
            body_prompts.append(line.replace("IMAGE_BODY_2:", "").strip())
        elif line.startswith("SOCIAL_CAPTION:"):
            social_caption = line.replace("SOCIAL_CAPTION:", "").strip()
        else:
            clean_lines.append(line)

    content = "\n".join(clean_lines).strip()
    match = re.search(r"<h1>(.*?)</h1>", content)
    if match:
        title = re.sub(r"<[^>]+>", "", match.group(1)).strip()

    return title, content, slug, keyphrase, metadesc, tags, cover_prompt, body_prompts, social_caption

def insert_images_in_content(content, body_images):
    """Inserisce le immagini nei placeholder del contenuto."""
    for i, img in enumerate(body_images):
        placeholder = "<!-- IMMAGINE INTERNA " + str(i+1) + " -->"
        wp_block = (
            "<!-- wp:image {\"id\":" + str(img["id"]) + "} -->\n"
            "<figure class=\"wp-block-image\">"
            "<img src=\"" + img["url"] + "\" class=\"wp-image-" + str(img["id"]) + "\"/>"
            "</figure>\n"
            "<!-- /wp:image -->"
        )
        content = content.replace(placeholder, wp_block, 1)
    # Rimuovi placeholder rimasti
    content = re.sub(r"<!-- IMMAGINE INTERNA \d+ -->", "", content)
    content = content.replace("<!-- IMMAGINE COPERTINA -->", "")
    return content

def send_telegram(caption, article_url):
    """Invia notifica su Telegram."""
    from config import TELEGRAM_TOKEN, TELEGRAM_CHAT, SOCIAL_ENABLED
    if not SOCIAL_ENABLED or not TELEGRAM_TOKEN or not TELEGRAM_CHAT:
        return
    try:
        text = caption + "\n\n" + article_url
        payload = json.dumps({"chat_id": TELEGRAM_CHAT, "text": text, "parse_mode": "HTML"}).encode()
        req = urllib.request.Request(
            "https://api.telegram.org/bot" + TELEGRAM_TOKEN + "/sendMessage",
            data=payload, method="POST"
        )
        req.add_header("Content-Type", "application/json")
        urllib.request.urlopen(req, timeout=15)
        print("  Telegram notifica inviata")
    except Exception as e:
        print("  Errore Telegram: " + str(e))

def run():
    print("=" * 55)
    print("  IncastroPC News Bot v3 — avvio")
    print("=" * 55)

    # 1. Raccolta RSS
    print("\n[1/5] Raccolta articoli RSS...")
    all_articles = fetch_all(hours_back=HOURS_BACK)
    stats["news_trovate"] = len(all_articles)
    stats["fonti_controllate"] = len([a for a in all_articles])

    # 2. Ranking e filtro duplicati
    print("\n[2/5] Ranking e controllo duplicati...")
    ranked = rank_articles(all_articles)
    stats["news_pertinenti"] = len(ranked)

    filtered = []
    for a in ranked:
        if a.get("score", 0) < MIN_SCORE:
            print("  Scartato (score basso): " + a["title"][:50])
            continue
        if is_duplicate(a):
            stats["duplicati"] += 1
            continue
        filtered.append(a)

    if not filtered:
        print("Nessuna news valida trovata. Uscita.")
        print_stats()
        sys.exit(0)

    print("News da elaborare: " + str(len(filtered)))

    # 3. Link interni
    print("\n[3/5] Ricerca link interni...")
    links_map = {}
    for i, a in enumerate(filtered, 1):
        links = find_internal_links(a["title"], a["summary"])
        if links:
            links_map[i] = links

    # 4. Generazione articoli
    print("\n[4/5] Generazione articoli...")
    digest_html = generate_digest(filtered, links_map)
    stats["news_generate"] = len(filtered)

    # 5. Pubblicazione
    print("\n[5/5] Pubblicazione su WordPress...")
    article_blocks = parse_articles(digest_html)
    consigliato_text = parse_consigliato(digest_html)

    published_url   = None
    published_title = None
    wp_info = []

    try:
        lines  = consigliato_text.strip().split("\n")
        numero = int(lines[0].strip()) - 1
        if 0 <= numero < len(article_blocks):
            block = article_blocks[numero]
            title, content, slug, keyphrase, metadesc, tags, cover_prompt, body_prompts, social_caption = extract_article_data(block)

            print("  Elaboro: " + title)

            # Genera immagini
            featured_media_id = None
            if cover_prompt:
                imgs = generate_article_images(title, cover_prompt, body_prompts[:IN_ARTICLE_IMAGES])
                featured_media_id = imgs.get("cover_id")
                body_images = imgs.get("body_images", [])
                content = insert_images_in_content(content, body_images)
            else:
                content = insert_images_in_content(content, [])

            # Pubblica su WordPress
            published_url = wp_publish(title, content, slug, keyphrase, metadesc, tags, featured_media_id)

            if published_url:
                stats["pubblicate"] += 1
                published_title = title
                wp_info = [(title, published_url)]

                # Aggiorna storico duplicati
                add_to_history(filtered[numero], published_url)

                # Telegram
                if social_caption:
                    send_telegram(social_caption, published_url)

    except Exception as e:
        print("  Errore pubblicazione: " + str(e))
        stats["errori"] += 1

    # Invia email
    send_digest(digest_html, wp_info)

    print_stats()
    print("\n✓ Bot completato!")

def print_stats():
    print("\n" + "=" * 40)
    print("  RIEPILOGO CICLO")
    print("=" * 40)
    print("  News trovate:     " + str(stats["news_trovate"]))
    print("  News pertinenti:  " + str(stats["news_pertinenti"]))
    print("  Duplicati:        " + str(stats["duplicati"]))
    print("  News generate:    " + str(stats["news_generate"]))
    print("  Pubblicate:       " + str(stats["pubblicate"]))
    print("  Errori:           " + str(stats["errori"]))
    print("=" * 40)

if __name__ == "__main__":
    run()
