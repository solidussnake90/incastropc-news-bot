import anthropic
import os
import base64
import urllib.request
import urllib.parse
import json

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = (
    "Sei il redattore capo di IncastroPC.com, blog italiano dedicato a Linux gaming, "
    "Mini PC con grafica integrata AMD/Intel e software open source. "
    "Per ogni notizia scrivi un articolo completo in italiano pronto per WordPress.\n\n"
    "STRUTTURA:\n"
    "1. Titolo SEO (50-65 caratteri)\n"
    "2. Intro (2 paragrafi)\n"
    "3. Corpo (3-5 paragrafi con H2)\n"
    "4. Sezione Cosa significa per IncastroPC (H2)\n"
    "5. Conclusione\n\n"
    "REGOLE:\n"
    "- Niente em-dash\n"
    "- Bold ogni 2-3 paragrafi\n"
    "- Italiano fluente, 400-600 parole per articolo\n"
    "- Niente tabelle\n\n"
    "FORMATO OBBLIGATORIO per ogni articolo:\n"
    "==INIZIO_ARTICOLO==\n"
    "<!-- wp:heading {\"level\":1} -->\n"
    "<h1>[Titolo]</h1>\n"
    "<!-- /wp:heading -->\n"
    "<!-- wp:paragraph -->\n"
    "<p>[testo]</p>\n"
    "<!-- /wp:paragraph -->\n"
    "<!-- wp:heading {\"level\":2} -->\n"
    "<h2>[titolo sezione]</h2>\n"
    "<!-- /wp:heading -->\n"
    "YOAST_KEYPHRASE: [keyphrase principale]\n"
    "YOAST_METADESC: [meta description 150-158 caratteri]\n"
    "YOAST_SLUG: [slug-url]\n"
    "IMAGE_COVER: [prompt inglese per copertina, esempio: dark linux gaming setup AMD GPU cinematic 16:9]\n"
    "IMAGE_BODY: [prompt inglese immagine interna, esempio: mini PC Linux penguin neon glow tech 16:9]\n"
    "==FINE_ARTICOLO==\n\n"
    "IMPORTANTE: usa SEMPRE ==INIZIO_ARTICOLO== e ==FINE_ARTICOLO== come delimitatori. "
    "Includi SEMPRE IMAGE_COVER e IMAGE_BODY con un prompt reale in inglese prima di ==FINE_ARTICOLO==.\n"
)


def generate_image(prompt, label="immagine"):
    try:
        api_key = os.environ.get("STABILITY_API_KEY")
        url = "https://api.stability.ai/v2beta/stable-image/generate/core"

        # Stability vuole multipart/form-data
        boundary = "----FormBoundary7MA4YWxkTrZu0gW"
        body = (
            "--" + boundary + "\r\n"
            "Content-Disposition: form-data; name=\"prompt\"\r\n\r\n"
            + prompt + ", cinematic lighting, high quality, sharp focus\r\n"
            "--" + boundary + "\r\n"
            "Content-Disposition: form-data; name=\"output_format\"\r\n\r\n"
            "jpeg\r\n"
            "--" + boundary + "\r\n"
            "Content-Disposition: form-data; name=\"aspect_ratio\"\r\n\r\n"
            "16:9\r\n"
            "--" + boundary + "--\r\n"
        ).encode("utf-8")

        req = urllib.request.Request(url, data=body, method="POST")
        req.add_header("Authorization", "Bearer " + api_key)
        req.add_header("Content-Type", "multipart/form-data; boundary=" + boundary)
        req.add_header("Accept", "image/*")

        with urllib.request.urlopen(req) as resp:
            img_bytes = resp.read()
            print("  Immagine ricevuta: " + str(len(img_bytes)) + " bytes")
            return base64.b64encode(img_bytes).decode("utf-8")

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print("  Errore HTTP " + str(e.code) + " per " + label + ": " + error_body[:300])
    except Exception as e:
        print("  Errore generazione " + label + ": " + str(e))
    return None


def generate_digest(articles):
    news_block = ""
    for i, a in enumerate(articles, 1):
        news_block += (
            "NOTIZIA " + str(i) + "\n"
            "Titolo: " + a["title"] + "\n"
            "Fonte: " + a["source"] + "\n"
            "URL: " + a["url"] + "\n"
            "Riassunto: " + a["summary"][:400] + "\n"
            "Punteggio: " + str(a["score"]) + "/100\n\n"
        )

    user_prompt = (
        "Ecco " + str(len(articles)) + " notizie gaming per IncastroPC.\n\n"
        + news_block +
        "Scrivi un articolo completo per ognuna. "
        "Usa ==INIZIO_ARTICOLO== e ==FINE_ARTICOLO== come delimitatori. "
        "Includi SEMPRE IMAGE_COVER e IMAGE_BODY con prompt reali in inglese. "
        "Inizia subito senza preamboli."
    )

    print("Invio a Claude API...")
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}]
    )
    raw_text = response.content[0].text
    print("Articoli generati: " + str(len(raw_text)) + " caratteri")

    import re
    article_blocks = re.findall(r"==INIZIO_ARTICOLO==(.*?)==FINE_ARTICOLO==", raw_text, re.DOTALL)
    print("Articoli trovati: " + str(len(article_blocks)))
    print("Prompt immagini trovati: " + str(raw_text.count("IMAGE_COVER:")))

    print("Generazione immagini con Stability AI...")
    enriched_blocks = []

    for i, block in enumerate(article_blocks):
        block = block.strip()
        cover_prompt = ""
        body_prompt = ""

        for line in block.split("\n"):
            if line.startswith("IMAGE_COVER:"):
                cover_prompt = line.replace("IMAGE_COVER:", "").strip()
            elif line.startswith("IMAGE_BODY:"):
                body_prompt = line.replace("IMAGE_BODY:", "").strip()

        print("  Articolo " + str(i+1) + " - Cover: " + cover_prompt[:60])

        if cover_prompt:
            print("  Generando copertina...")
            cover_b64 = generate_image(cover_prompt, "copertina")
            if cover_b64:
                block += "\nCOVER_IMAGE_B64: " + cover_b64
                print("  Copertina OK")

        if body_prompt:
            print("  Generando immagine interna...")
            body_b64 = generate_image(body_prompt, "interna")
            if body_b64:
                block += "\nBODY_IMAGE_B64: " + body_b64
                print("  Immagine interna OK")

        enriched_blocks.append(block)

    result = ""
    for block in enriched_blocks:
        result += "<!-- ARTICOLO -->\n" + block + "\n---\n"

    return result
