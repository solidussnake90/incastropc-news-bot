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
    "4. Sezione Cosa significa per IncastroPC (H2)\n"
    "5. Conclusione\n\n"
    "REGOLE:\n"
    "- Niente em-dash\n"
    "- Bold ogni 2-3 paragrafi\n"
    "- Italiano fluente, 400-600 parole per articolo\n"
    "- Niente tabelle\n\n"
    "FORMATO OBBLIGATORIO per ogni articolo:\n"
    "<!-- ARTICOLO [numero]: [Titolo] -->\n"
    "<!-- wp:heading {\"level\":1} -->\n"
    "<h1>[Titolo]</h1>\n"
    "<!-- /wp:heading -->\n"
    "<!-- wp:paragraph -->\n"
    "<p>[testo]</p>\n"
    "<!-- /wp:paragraph -->\n"
    "<!-- wp:heading {\"level\":2} -->\n"
    "<h2>[titolo sezione]</h2>\n"
    "<!-- /wp:heading -->\n"
    "<!-- FINE ARTICOLO [numero] -->\n"
    "---\n"
    "YOAST_KEYPHRASE: [keyphrase principale]\n"
    "YOAST_METADESC: [meta description 150-158 caratteri]\n"
    "YOAST_SLUG: [slug-url]\n"
    "IMAGE_COVER: [prompt inglese per copertina, esempio: dark linux gaming setup with glowing AMD GPU, cinematic 16:9]\n"
    "IMAGE_BODY: [prompt inglese per immagine interna, esempio: mini PC with Linux penguin neon glow tech illustration 16:9]\n\n"
    "IMPORTANTE: devi SEMPRE includere IMAGE_COVER e IMAGE_BODY alla fine di ogni articolo, dopo YOAST_SLUG. "
    "Sono obbligatori per generare le immagini automaticamente.\n"
)


def generate_image(prompt, label="immagine"):
    try:
        from google import genai
        gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash-preview-image-generation",
            contents="Generate a high quality 16:9 image: " + prompt,
            config={"response_modalities": ["IMAGE"]},
        )
        for part in response.candidates[0].content.parts:
            if hasattr(part, "inline_data") and part.inline_data:
                return base64.b64encode(part.inline_data.data).decode("utf-8")
        print("  Nessuna immagine nei risultati per " + label)
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
        "\nScrivi un articolo completo in italiano per ognuna. "
        "Ricorda: includi SEMPRE IMAGE_COVER e IMAGE_BODY alla fine di ogni articolo. "
        "Inizia subito con il primo articolo senza preamboli."
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

    cover_count = raw_text.count("IMAGE_COVER:")
    print("Prompt immagini trovati: " + str(cover_count))

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

        print("  Cover prompt: " + cover_prompt[:60] + "...")

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

    return "---".join(enriched_blocks)
