import anthropic
from google import genai
from google.genai import types
import os
import base64
from config import ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

SYSTEM_PROMPT = """Sei il redattore capo di IncastroPC.com, blog italiano dedicato a Linux gaming, 
Mini PC con grafica integrata AMD/Intel e software open source. Il tuo pubblico è tecnico ma non estremo — 
appassionati che vogliono giocare su hardware accessibile con Linux.

Per ogni notizia che ricevi devi scrivere un ARTICOLO COMPLETO in italiano, pronto per essere pubblicato 
su WordPress con minime modifiche. 

STRUTTURA OBBLIGATORIA DI OGNI ARTICOLO:
1. Titolo SEO (50-65 caratteri, include la keyword principale)
2. Intro (2 paragrafi): primo con una scena concreta o fatto sorprendente che aggancia il lettore, 
   secondo che contestualizza la notizia per il pubblico IncastroPC
3. Corpo dell'articolo (3-5 paragrafi con H2): sviluppa la notizia, aggiungi contesto tecnico, 
   spiega le implicazioni per chi usa Linux o Mini PC con iGPU AMD/Intel
4. Sezione "Cosa significa per IncastroPC" (H2)
5. Conclusione (1 paragrafo)

REGOLE STILISTICHE:
- Niente em-dash o trattini narrativi
- Bold ogni 2-3 paragrafi su concetti chiave
- Tono diretto, italiano fluente
- Lunghezza: 400-600 parole per articolo
- Niente tabelle, niente separatori orizzontali

Alla fine di ogni articolo aggiungi:
IMAGE_COVER: [prompt inglese per immagine di copertina, stile cinematografico, 16:9, gaming/tech]
IMAGE_BODY: [prompt inglese per immagine interna, stile tech illustration, 16:9]

FORMATO OUTPUT HTML Gutenberg per ogni articolo:

<!-- ARTICOLO [numero]: [Titolo] -->
<!-- wp:heading {"level":1} -->
<h1>[Titolo SEO]</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>[contenuto]</p>
<!-- /wp:paragraph -->

<!-- wp:heading {"level":2} -->
<h2>[Titolo sezione]</h2>
<!-- /wp:heading -->

<!-- FINE ARTICOLO [numero] -->
---
YOAST_KEYPHRASE: [focus keyphrase]
YOAST_METADESC: [meta description 150-158 caratteri]
YOAST_SLUG: [slug-url-articolo]
IMAGE_COVER: [prompt copertina]
IMAGE_BODY: [prompt immagine interna]
"""

def generate_image(prompt, label="immagine"):
    """Genera un'immagine con Gemini e restituisce base64."""
    try:
        gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        response = gemini_client.models.generate_image(
            model="imagen-3.0-generate-002",
            prompt=f"High quality image: {prompt}. Style: cinematic, professional, tech gaming aesthetic.",
            config=types.GenerateImageConfig(
                number_of_images=1,
                aspect_ratio="16:9",
            )
        )
        if response.generated_images:
            img_data = response.generated_images[0].image.image_bytes
            return base64.b64encode(img_data).decode('utf-8')
    except Exception as e:
        print(f"  ✗ Errore generazione {label}: {e}")
    return None
---
NOTIZIA {i}
Titolo originale: {a['title']}
Fonte: {a['source']}
URL originale: {a['url']}
Riassunto: {a['summary'][:600]}
Punteggio rilevanza IncastroPC: {a['score']}/100
"""

    user_prompt = f"""Ecco le {len(articles)} notizie gaming più rilevanti delle ultime 24 ore per IncastroPC.

{news_block}

Scrivi un articolo completo in italiano per ognuna delle {len(articles)} notizie, 
seguendo esattamente la struttura e le regole editoriali di IncastroPC.
Inizia direttamente con il primo articolo, senza preamboli."""

    print("Invio a Claude API...")
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}]
    )
    raw_text = response.content[0].text
    print(f"Articoli generati: {len(raw_text)} caratteri")

    # Genera immagini per ogni articolo
    print("Generazione immagini con Gemini...")
    blocks = raw_text.split("---")
    enriched_blocks = []

    for block in blocks:
        block = block.strip()
        if not block or "<!-- ARTICOLO" not in block:
            enriched_blocks.append(block)
            continue

        # Estrai prompt immagini
        cover_prompt = ""
        body_prompt = ""
        for line in block.split("\n"):
            if line.startswith("IMAGE_COVER:"):
                cover_prompt = line.replace("IMAGE_COVER:", "").strip()
            elif line.startswith("IMAGE_BODY:"):
                body_prompt = line.replace("IMAGE_BODY:", "").strip()

        # Genera immagini
        cover_b64 = None
        body_b64 = None
        if cover_prompt:
            print(f"  Generando copertina...")
            cover_b64 = generate_image(cover_prompt, "copertina")
        if body_prompt:
            print(f"  Generando immagine interna...")
            body_b64 = generate_image(body_prompt, "interna")

        # Aggiungi immagini al blocco
        if cover_b64:
            block += f"\nCOVER_IMAGE_B64: {cover_b64}"
        if body_b64:
            block += f"\nBODY_IMAGE_B64: {body_b64}"

        enriched_blocks.append(block)

    return "---".join(enriched_blocks)
