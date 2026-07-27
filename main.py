import sys
from collector import fetch_all
from ranker    import rank_articles
from writer    import generate_digest
from mailer    import send_digest

def run():
    print("=" * 50)
    print("  IncastroPC News Bot — avvio")
    print("=" * 50)

    print("\n[1/4] Raccolta articoli RSS...")
    articles = fetch_all(hours_back=24)

    if not articles:
        print("Nessun articolo trovato. Uscita.")
        sys.exit(0)

    print("\n[2/4] Ranking per rilevanza...")
    top_articles = rank_articles(articles)

    print("\n[3/4] Generazione articoli con Claude...")
    digest_html = generate_digest(top_articles)

    print("\n[4/4] Invio email...")
    send_digest(digest_html)

    print("\n✓ Bot completato con successo!")

if __name__ == "__main__":
    run()
