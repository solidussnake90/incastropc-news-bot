import anthropic
from config import ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

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
"""

def generate_digest(articles):
    news_block = ""
    for i, a in enumerate(articles, 1):
        news_block += f"""
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

    digest_html = response.content[0].text
    print(f"Articoli generati: {len(digest_html)} caratteri")
    return digest_html
