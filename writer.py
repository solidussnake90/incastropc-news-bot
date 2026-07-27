import anthropic
import os

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
    "IMAGE_COVER: [prompt inglese dettagliato per immagine copertina, stile cinematografico 16:9]\n"
    "IMAGE_BODY: [prompt inglese dettagliato per immagine interna, stile tech illustration 16:9]\n"
    "==FINE_ARTICOLO==\n\n"
    "Includi SEMPRE IMAGE_COVER e IMAGE_BODY con prompt reali e dettagliati in inglese.\n"
)


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
        "Includi SEMPRE IMAGE_COVER e IMAGE_BODY con prompt reali e dettagliati in inglese. "
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

    result = ""
    for block in article_blocks:
        result += "<!-- ARTICOLO -->\n" + block.strip() + "\n---\n"

    return result
