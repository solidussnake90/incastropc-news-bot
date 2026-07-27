import anthropic
import os
import base64

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = (
    "Sei il redattore capo di IncastroPC.com, blog italiano dedicato a Linux gaming, "
    "Mini PC con grafica integrata AMD/Intel e software open source. "
    "Per ogni notizia scrivi un articolo completo in italiano pronto per WordPress.\n\n"
    "STRUTTURA:\n"
    "1. Titolo SEO (50-65 caratteri)\n"
    "2. Intro (2 paragrafi)\n"
    "3. Corpo (3-5 paragrafi con H2)\n"
    "4. Sezione 'Cosa significa per IncastroPC' (H2)\n"
    "5. Conclusione\n\n"
    "REGOLE:\n"
    "- Niente em-dash\n"
    "- Bold ogni 2-3 paragrafi\n"
    "- Italiano fluente, 400-600 parole per articolo\n"
    "- Niente tabelle\n\n"
    "FORMATO per ogni articolo:\n"
    "<!-- ARTICOLO [numero]: [Titolo] -->\n"
    "<!-- wp:heading {\"level\":1} -->\n"
    "<h1>[Titolo]</h1>\n"
    "<!-- /wp:heading -->\n"
    "<!-- wp:paragraph -->\n"
    "<p>[testo]</p>\n"
    "<!-- /wp:paragraph -->\n"
    "<!-- FINE ARTICOLO [numero] -->\n"
    "---\n"
    "YOAST_KEYPHRASE: [keyphrase]\n"
    "YOAST_METADESC: [meta 150-158 caratteri]\n"
    "YOAST_SLUG: [slug]\n"
    "IMAGE_COVER: [prompt inglese per immagine copertina cinematografica 16:9]\n"
    "IMAGE_BODY: [prompt inglese per immagine interna tech illustration]\n"
)


def generate_image(prompt, label="immagine"):
    try:
        from google import genai
        from google.genai import types
        gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        response = gemini_client.models.generate_image(
            model="imagen-3.0-generate-002",
            prompt="High quality image: " + prompt + ". Style: cinematic, professional, tech gaming.",
            config=types.GenerateImageConfig(
                number_of_images=1,
                aspect_ratio="16:9",
            )
        )
        if response.generated_images:
            img_data = response.generated_images[0].image.image_bytes
            return base64.b64encode(img_data).decode("utf-8")
    except Exception as e:
        print("  Errore generazione " + label + ": " + str(e))
    return None


def generate_digest(articles):
    news_block = ""
    for i, a in enumerate(articles, 1):
        news_block += (
            "---\n"
            "NOTIZIA " + str(i) + "\n"
            "Titolo: " + a["title"] + "\n"
            "Fonte: " + a["source"] + "\n"
            "URL: " + a["url"] + "\n"
            "Riassunto: " + a["summary"][:400] + "\n"
            "Punteggio: " + str(a["score"]) + "/100\n"
        )

    user_prompt = (
        "Ecco " + str(len(articles)) + " notizie gaming delle ultime 24 ore per IncastroPC.\n\n"
        + news_block +
        "\nScrivi un articolo completo per ognuna. Inizia subito senza preamboli."
    )

    print("Invio a Claude API...")
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}]
    )
    raw_text = response.content[0].text
    print("Articoli generati: " + str(len(raw_text)) + " caratteri")

    # Genera immagini con Gemini
    print("Generazione immagini con Gemini...")
    blocks = raw_text.split("---")
    enriched_blocks = []

    for block in blocks:
        block = block.strip()
        if not block or "<!-- ARTICOLO" not in block:
            enriched_blocks.append(block)
            continue

        cover_prompt = ""
        body_prompt = ""
        for line in block.split("\n"):
            if line.startswith("IMAGE_COVER:"):
                cover_prompt = line.replace("IMAGE_COVER:", "").strip()
            elif line.startswith("IMAGE_BODY:"):
                body_prompt = line.replace("IMAGE_BODY:", "").strip()

        if cover_prompt:
            print("  Generando copertina...")
            cover_b64 = generate_image(cover_prompt, "copertina")
            if cover_b64:
                block += "\nCOVER_IMAGE_B64: " + cover_b64

        if body_prompt:
            print("  Generando immagine interna...")
            body_b64 = generate_image(body_prompt, "interna")
            if body_b64:
                block += "\nBODY_IMAGE_B64: " + body_b64

        enriched_blocks.append(block)

    return "---".join(enriched_blocks)
