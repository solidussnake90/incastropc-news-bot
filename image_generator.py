import urllib.request
import urllib.parse
import urllib.error
import json
import base64
import os
import time
from config import IMAGE_PROVIDER, IMAGE_WIDTH, IMAGE_HEIGHT, WP_URL, WP_USERNAME, WP_PASSWORD, WP_TIMEOUT

def generate_image_pollinations(prompt, width=1200, height=630):
    """Genera immagine con Pollinations.ai (gratuito, no API key)."""
    try:
        clean_prompt = prompt.replace('"', '').replace("'", '')[:200]
        encoded = urllib.parse.quote(clean_prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&nologo=true&model=flux"

        req = urllib.request.Request(url)
        req.add_header("User-Agent", "IncastroPC-Bot/1.0")

        with urllib.request.urlopen(req, timeout=60) as resp:
            img_data = resp.read()
            if len(img_data) > 1000:
                print("  Immagine generata: " + str(len(img_data)) + " bytes")
                return img_data
    except Exception as e:
        print("  Errore Pollinations: " + str(e))
    return None

def upload_to_wp_media(img_data, filename, alt_text=""):
    """Carica immagine nella Media Library di WordPress."""
    if not WP_URL or not WP_USERNAME or not WP_PASSWORD:
        return None

    try:
        credentials = base64.b64encode((WP_USERNAME + ":" + WP_PASSWORD).encode()).decode()
        url = WP_URL + "/wp-json/wp/v2/media"

        req = urllib.request.Request(url, data=img_data, method="POST")
        req.add_header("Authorization", "Basic " + credentials)
        req.add_header("Content-Type", "image/jpeg")
        req.add_header("Content-Disposition", 'attachment; filename="' + filename + '"')

        with urllib.request.urlopen(req, timeout=WP_TIMEOUT) as resp:
            result = json.loads(resp.read())
            media_id  = result.get("id")
            media_url = result.get("source_url", "")

            # Imposta alt text
            if alt_text and media_id:
                update_data = json.dumps({"alt_text": alt_text}).encode()
                update_req = urllib.request.Request(
                    WP_URL + "/wp-json/wp/v2/media/" + str(media_id),
                    data=update_data,
                    method="POST"
                )
                update_req.add_header("Authorization", "Basic " + credentials)
                update_req.add_header("Content-Type", "application/json")
                urllib.request.urlopen(update_req, timeout=WP_TIMEOUT)

            print("  Immagine caricata su WP: " + str(media_id))
            return {"id": media_id, "url": media_url}

    except Exception as e:
        print("  Errore upload WP media: " + str(e))
    return None

def generate_and_upload(prompt, filename, alt_text="", width=1200, height=630):
    """Genera immagine e la carica su WordPress. Restituisce {id, url} o None."""
    if IMAGE_PROVIDER == "none":
        return None

    print("  Generando immagine: " + prompt[:60] + "...")

    img_data = None
    if IMAGE_PROVIDER in ("pollinations", "local"):
        img_data = generate_image_pollinations(prompt, width, height)

    if img_data:
        time.sleep(1)  # evita rate limiting
        return upload_to_wp_media(img_data, filename, alt_text)

    return None

def generate_article_images(article_title, cover_prompt, body_prompts):
    """
    Genera tutte le immagini per un articolo.
    Restituisce {cover_id, cover_url, body_images: [{id, url}]}
    """
    result = {"cover_id": None, "cover_url": None, "body_images": []}

    # Immagine copertina
    cover = generate_and_upload(
        prompt=cover_prompt,
        filename="cover-" + article_title[:30].replace(" ", "-").lower() + ".jpg",
        alt_text=article_title,
        width=IMAGE_WIDTH,
        height=IMAGE_HEIGHT
    )
    if cover:
        result["cover_id"] = cover["id"]
        result["cover_url"] = cover["url"]

    # Immagini interne
    from config import IN_ARTICLE_IMAGES
    for i, prompt in enumerate(body_prompts[:IN_ARTICLE_IMAGES]):
        time.sleep(2)  # pausa tra generazioni
        img = generate_and_upload(
            prompt=prompt,
            filename="body-" + str(i+1) + "-" + article_title[:20].replace(" ", "-").lower() + ".jpg",
            alt_text=article_title + " - immagine " + str(i+1),
            width=900,
            height=500
        )
        if img:
            result["body_images"].append(img)

    return result
