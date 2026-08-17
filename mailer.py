import smtplib
import datetime
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import SMTP_HOST, SMTP_PORT, EMAIL_FROM, EMAIL_PASSWORD, EMAIL_TO

EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  body {{ font-family: -apple-system, Arial, sans-serif; background: #f5f5f5; margin: 0; padding: 20px; }}
  .container {{ max-width: 780px; margin: 0 auto; background: #fff; border-radius: 8px; overflow: hidden; }}
  .header {{ background: #0a0a14; padding: 28px 32px; }}
  .header h1 {{ color: #FFD700; margin: 0; font-size: 22px; letter-spacing: 1px; }}
  .header p {{ color: rgba(255,255,255,0.5); margin: 6px 0 0; font-size: 13px; }}
  .content {{ padding: 32px; }}
  .consigliato-box {{ background: #0a0a14; border: 2px solid #FFD700; border-radius: 8px; padding: 20px 24px; margin-bottom: 32px; }}
  .consigliato-box .badge {{ background: #FFD700; color: #000; font-weight: 700; font-size: 12px; padding: 3px 12px; border-radius: 20px; display: inline-block; margin-bottom: 10px; }}
  .consigliato-box h2 {{ color: #FFD700; margin: 0 0 8px; font-size: 16px; }}
  .consigliato-box p {{ color: rgba(255,255,255,0.85); margin: 0; font-size: 14px; line-height: 1.5; }}
  .wp-links-box {{ background: #f0fff0; border: 1px solid #90EE90; border-radius: 6px; padding: 16px 20px; margin-bottom: 24px; }}
  .wp-links-box h3 {{ margin: 0 0 10px; font-size: 14px; color: #2a7a2a; }}
  .wp-links-box a {{ display: block; color: #2a7a2a; text-decoration: none; font-size: 13px; margin-bottom: 6px; font-weight: 600; }}
  .article-block {{ border: 1px solid #e8e8e8; border-radius: 6px; margin-bottom: 40px; overflow: hidden; }}
  .article-header {{ background: #0a0a14; padding: 14px 20px; }}
  .article-num {{ background: #FFD700; color: #000; font-weight: 700; font-size: 13px; padding: 3px 10px; border-radius: 3px; }}
  .article-body {{ padding: 24px; background: #fff; }}
  .article-body h1 {{ font-size: 20px; color: #111; margin: 0 0 16px; line-height: 1.3; }}
  .article-body h2 {{ font-size: 16px; color: #222; margin: 20px 0 10px; border-left: 3px solid #FFD700; padding-left: 10px; }}
  .article-body p {{ font-size: 14px; color: #444; line-height: 1.7; margin: 0 0 12px; }}
  .article-body strong {{ color: #111; }}
  .seo-block {{ background: #f9f9f0; border: 1px solid #ddd; border-radius: 4px; padding: 12px 16px; margin-top: 16px; font-size: 12px; color: #555; }}
  .image-block {{ background: #f5f5ff; border: 1px solid #ddd; border-radius: 4px; padding: 12px 16px; margin-top: 12px; font-size: 12px; color: #444; }}
  .prompt {{ font-family: monospace; background: #eeeeff; padding: 6px 10px; border-radius: 3px; display: block; margin-top: 4px; color: #333; font-size: 11px; }}
  .firefly-link {{ display: inline-block; margin-top: 8px; background: #333; color: #fff; padding: 4px 12px; border-radius: 3px; text-decoration: none; font-size: 11px; font-weight: 700; }}
  .footer {{ background: #f9f9f9; padding: 20px 32px; font-size: 12px; color: #aaa; border-top: 1px solid #eee; text-align: center; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>⚡ IncastroPC Gaming News</h1>
    <p>{count} articoli pronti per WordPress · {date}</p>
  </div>
  <div class="content">
    {consigliato_html}
    {wp_links_html}
    {articles_html}
  </div>
  <div class="footer">Generato da IncastroPC Gaming Bot · {date}</div>
</div>
</body>
</html>
"""

def clean_raw_text(raw_text):
    return re.sub(r"==CONSIGLIATO==.*?==FINE_CONSIGLIATO==", "", raw_text, flags=re.DOTALL)

def parse_consigliato(raw_text):
    match = re.search(r"==CONSIGLIATO==(.*?)==FINE_CONSIGLIATO==", raw_text, re.DOTALL)
    return match.group(1).strip() if match else ""

def parse_articles(raw_text):
    cleaned = clean_raw_text(raw_text)
    articles = []
    for block in cleaned.split("---"):
        block = block.strip()
        if block and "<!-- ARTICOLO -->" in block:
            articles.append(block.replace("<!-- ARTICOLO -->", "").strip())
    return articles

def format_consigliato_html(consigliato_text, articles):
    if not consigliato_text:
        return ""
    lines = consigliato_text.strip().split("\n")
    numero = lines[0].strip() if lines else "1"
    motivazione = " ".join(lines[1:]).strip() if len(lines) > 1 else ""
    titolo = ""
    try:
        idx = int(numero) - 1
        if 0 <= idx < len(articles):
            match = re.search(r"<h1>(.*?)</h1>", articles[idx])
            if match:
                titolo = match.group(1)
    except:
        pass
    return (
        '<div class="consigliato-box">'
        '<span class="badge">⭐ PUBBLICA OGGI — Articolo ' + numero + '</span>'
        '<h2>' + titolo + '</h2>'
        '<p>' + motivazione + '</p>'
        '</div>'
    )

def format_wp_links_html(wp_links):
    if not wp_links:
        return ""
    html = '<div class="wp-links-box"><h3>✅ Articolo pubblicato su WordPress</h3>'
    for title, link in wp_links:
        if title and link:
            html += '<a href="' + link + '" target="_blank">🔗 ' + title + '</a>'
    html += '</div>'
    return html

def format_article_html(block, index):
    yoast_kp = yoast_meta = yoast_slug = image_cover = image_body = ""
    clean_lines = []
    for line in block.split("\n"):
        if line.startswith("YOAST_KEYPHRASE:"):
            yoast_kp = line.replace("YOAST_KEYPHRASE:", "").strip()
        elif line.startswith("YOAST_METADESC:"):
            yoast_meta = line.replace("YOAST_METADESC:", "").strip()
        elif line.startswith("YOAST_SLUG:"):
            yoast_slug = line.replace("YOAST_SLUG:", "").strip()
        elif line.startswith("IMAGE_COVER:"):
            image_cover = line.replace("IMAGE_COVER:", "").strip()
        elif line.startswith("IMAGE_BODY:"):
            image_body = line.replace("IMAGE_BODY:", "").strip()
        else:
            clean_lines.append(line)
    article_html = "\n".join(clean_lines).strip()
    seo_block = ""
    if yoast_kp or yoast_meta or yoast_slug:
        seo_block = '<div class="seo-block"><strong>🎯 Yoast SEO</strong><br><b>Keyphrase:</b> ' + yoast_kp + '<br><b>Meta:</b> ' + yoast_meta + '<br><b>Slug:</b> ' + yoast_slug + '</div>'
    image_block = ""
    if image_cover or image_body:
        image_block = '<div class="image-block"><strong>🎨 Prompt immagini — Adobe Firefly</strong>'
        if image_cover:
            image_block += '<b>Copertina:</b><span class="prompt">' + image_cover + '</span>'
        if image_body:
            image_block += '<b style="display:block;margin-top:8px;">Immagine interna:</b><span class="prompt">' + image_body + '</span>'
        image_block += '<br><a href="https://firefly.adobe.com" class="firefly-link" target="_blank">→ Apri Adobe Firefly</a></div>'
    return (
        '<div class="article-block">'
        '<div class="article-header"><span class="article-num">Articolo ' + str(index) + '</span></div>'
        '<div class="article-body">' + article_html + seo_block + image_block + '</div>'
        '</div>'
    )

def send_digest(raw_text, wp_links=None):
    today = datetime.date.today().strftime("%d %B %Y")
    consigliato_text = parse_consigliato(raw_text)
    article_blocks = parse_articles(raw_text)
    consigliato_html = format_consigliato_html(consigliato_text, article_blocks)
    wp_links_html = format_wp_links_html(wp_links or [])
    if not article_blocks:
        articles_html = "<pre style='font-size:12px;'>" + raw_text[:3000] + "</pre>"
        count = "0"
    else:
        articles_html = "".join(format_article_html(b, i+1) for i, b in enumerate(article_blocks))
        count = str(len(article_blocks))
    html_body = EMAIL_TEMPLATE.format(
        articles_html=articles_html,
        consigliato_html=consigliato_html,
        wp_links_html=wp_links_html,
        count=count,
        date=today
    )
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "⚡ IncastroPC Gaming News — " + today
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg.attach(MIMEText(html_body, "html"))
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
    print("Email inviata a " + EMAIL_TO)
