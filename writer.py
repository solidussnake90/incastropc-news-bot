import os
import urllib.request
import urllib.error
import json

from config import ANTHROPIC_API_KEY, AI_PROVIDER, OLLAMA_MODEL, OLLAMA_URL

def call_anthropic(system_prompt, user_prompt, max_tokens=16000):
    """Chiama Claude API."""
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )
    return response.content[0].text

def call_ollama(system_prompt, user_prompt):
    """Chiama modello locale via Ollama."""
    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": system_prompt + "\n\n" + user_prompt,
        "stream": False,
        "options": {"num_predict": 8000, "temperature": 0.7}
    }).encode("utf-8")

    req = urllib.request.Request(OLLAMA_URL + "/api/generate", data=payload, method="POST")
    req.add_header("Content-Type", "application/json")

    with urllib.request.urlopen(req, timeout=300) as resp:
        result = json.loads(resp.read())
        return result.get("response", "")

def call_ai(system_prompt, user_prompt):
    """Chiama il provider AI configurato."""
    provider = AI_PROVIDER.lower()

    if provider == "local":
        print("  Usando AI locale (Ollama)...")
        try:
            return call_ollama(system_prompt, user_prompt)
        except Exception as e:
            print("  Errore AI locale: " + str(e))
            return ""

    elif provider == "hybrid":
        print("  Usando AI locale (Ollama)...")
        try:
            result = call_ollama(system_prompt, user_prompt)
            if result and len(result) > 100:
                return result
        except Exception as e:
            print("  AI locale fallita, uso Anthropic: " + str(e))
        print("  Fallback su Anthropic...")
        return call_anthropic(system_prompt, user_prompt)

    else:  # anthropic (default)
        print("  Usando Anthropic Claude...")
        return call_anthropic(system_prompt, user_prompt)

SYSTEM_PROMPT = (
    "Sei il redattore di IncastroPC.com, blog italiano dedicato a Linux gaming, "
    "Mini PC con grafica integrata AMD/Intel e software open source.\n\n"
    "LA FILOSOFIA: rendere Linux facile e accessibile a tutti.\n\n"
    "ANTI-ALLUCINAZIONE — REGOLA ASSOLUTA:\n"
    "NON inventare MAI date, prezzi, specifiche, dichiarazioni, benchmark, FPS, "
    "versioni, disponibilita' o citazioni. Scrivi SOLO cio' che e' nella notizia. "
    "Se le informazioni sono insufficienti, l'articolo sara' breve ma accurato.\n\n"
    "TIPO DI ARTICOLI: news giornaliere concrete.\n\n"
    "STRUTTURA OBBLIGATORIA:\n"
    "1. Titolo SEO 50-65 caratteri\n"
    "2. Primo paragrafo: notizia concreta. Cosa, quando, chi\n"
    "3. Secondo paragrafo: cos'e' questo software/hardware per chi non lo conosce\n"
    "4. H2 breve e specifico (max 5 parole): dettagli tecnici\n"
    "5. Paragrafo dettagli\n"
    "6. H2 breve e creativo (max 5 parole): impatto pratico\n"
    "   NON usare: 'Cosa significa per Linux', 'Perche importa', 'Impatto su Linux'\n"
    "7. Paragrafo impatto\n"
    "8. Shortcode [incastro_minipc_random]\n"
    "9. Paragrafo finale con link interni in stile 'leggi qui: [titolo]'\n"
    "   USA SOLO i link interni forniti nella sezione LINK INTERNI DISPONIBILI\n"
    "   Se non sono forniti link, non inserire link interni\n\n"
    "ARTICOLO CONSIGLIATO:\n"
    "Dopo tutti gli articoli aggiungi:\n"
    "==CONSIGLIATO==\n"
    "[numero articolo]\n"
    "[motivazione 1-2 righe]\n"
    "==FINE_CONSIGLIATO==\n\n"
    "FORMATO per ogni articolo:\n"
    "==INIZIO_ARTICOLO==\n"
    "<!-- wp:heading {\"level\":1} -->\n"
    "<h1>[Titolo]</h1>\n"
    "<!-- /wp:heading -->\n"
    "<!-- IMMAGINE COPERTINA -->\n"
    "<!-- wp:paragraph -->\n"
    "<p>[Primo paragrafo]</p>\n"
    "<!-- /wp:paragraph -->\n"
    "<!-- wp:paragraph -->\n"
    "<p>[Secondo paragrafo]</p>\n"
    "<!-- /wp:paragraph -->\n"
    "<!-- wp:heading {\"level\":2} -->\n"
    "<h2>[H2 dettagli]</h2>\n"
    "<!-- /wp:heading -->\n"
    "<!-- wp:paragraph -->\n"
    "<p>[Dettagli]</p>\n"
    "<!-- /wp:paragraph -->\n"
    "<!-- IMMAGINE INTERNA 1 -->\n"
    "<!-- wp:heading {\"level\":2} -->\n"
    "<h2>[H2 impatto]</h2>\n"
    "<!-- /wp:heading -->\n"
    "<!-- wp:paragraph -->\n"
    "<p>[Impatto]</p>\n"
    "<!-- /wp:paragraph -->\n"
    "<!-- IMMAGINE INTERNA 2 -->\n"
    "[incastro_minipc_random]\n"
    "<!-- wp:paragraph -->\n"
    "<p>[Paragrafo finale con link interni]</p>\n"
    "<!-- /wp:paragraph -->\n"
    "YOAST_KEYPHRASE: [max 4 parole]\n"
    "YOAST_METADESC: [140-156 caratteri]\n"
    "YOAST_EXCERPT: [riassunto breve max 155 caratteri, diverso dalla meta]\n"
    "YOAST_SLUG: [slug-kebab-case]\n"
    "YOAST_TAGS: [tag1, tag2, tag3, tag4, tag5]\n"
    "IMAGE_COVER: [prompt inglese copertina cinematografica 16:9, no text in image]\n"
    "IMAGE_BODY_1: [prompt inglese immagine interna 1, diverso dalla copertina, no text]\n"
    "IMAGE_BODY_2: [prompt inglese immagine interna 2, diverso dalle precedenti, no text]\n"
    "SOCIAL_CAPTION: [caption italiana per Telegram/social: hook + spiegazione + CTA + link + hashtag]\n"
    "==FINE_ARTICOLO==\n"
)


def generate_digest(articles, internal_links_map=None):
    """
    Genera articoli per tutte le news.
    internal_links_map: dict {article_index: [link_objects]}
    """
    import re

    news_block = ""
    for i, a in enumerate(articles, 1):
        links_text = ""
        if internal_links_map and i in internal_links_map:
            links = internal_links_map[i]
            if links:
                links_text = "\nLINK INTERNI DISPONIBILI:\n"
                for l in links:
                    links_text += "- " + l["title"] + " → " + l["url"] + "\n"

        news_block += (
            "NEWS " + str(i) + "\n"
            "Titolo originale: " + a["title"] + "\n"
            "Fonte: " + a["source"] + "\n"
            "URL fonte: " + a["url"] + "\n"
            "Data: " + str(a["published"]) + "\n"
            "Riassunto: " + a["summary"][:600] + "\n"
            + links_text + "\n"
        )

    user_prompt = (
        "Ecco " + str(len(articles)) + " news per IncastroPC.\n\n"
        + news_block +
        "\nScrivi un articolo italiano per ognuna. "
        "Basa il contenuto SOLO sui fatti forniti. "
        "Non inventare nulla. "
        "H2 creativi e specifici. "
        "400-700 parole per articolo. "
        "Alla fine scegli l'articolo consigliato. "
        "Inizia subito."
    )

    print("Generazione articoli con " + AI_PROVIDER + "...")
    raw_text = call_ai(SYSTEM_PROMPT, user_prompt)
    print("Articoli generati: " + str(len(raw_text)) + " caratteri")

    article_blocks = re.findall(r"==INIZIO_ARTICOLO==(.*?)==FINE_ARTICOLO==", raw_text, re.DOTALL)
    print("Articoli trovati: " + str(len(article_blocks)))

    consigliato = re.search(r"==CONSIGLIATO==(.*?)==FINE_CONSIGLIATO==", raw_text, re.DOTALL)
    consigliato_text = consigliato.group(1).strip() if consigliato else ""

    result = ""
    if consigliato_text:
        result += "==CONSIGLIATO==\n" + consigliato_text + "\n==FINE_CONSIGLIATO==\n"

    for block in article_blocks:
        result += "<!-- ARTICOLO -->\n" + block.strip() + "\n---\n"

    return result
