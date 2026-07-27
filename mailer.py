import smtplib
import datetime
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
  .article-block {{ border: 1px solid #e8e8e8; border-radius: 6px; margin-bottom: 40px; overflow: hidden; }}
  .article-header {{ background: #0a0a14; padding: 14px 20px; }}
  .article-num {{ background: #FFD700; color: #000; font-weight: 700; font-size: 13px; padding: 3px 10px; border-radius: 3px; }}
  .cover-img {{ width: 100%; height: 220px; object-fit: cover; display: block; }}
  .body-img {{ width: 100%; max-height: 180px; object-fit: cover; display: block; margin: 16px 0; border-radius: 4px; }}
  .article-body {{ padding: 24px; }}
  .article-body h1 {{ font-size: 20px; color: #111; margin: 0 0 16px; line-height: 1.3; }}
  .article-body h2 {{ font-size: 16px; color: #222; margin: 20px 0 10px; border-left: 3px solid #FFD700; padding-left: 10px; }}
  .article-body p {{ font-size: 14px; color: #444; line-height: 1.7; margin: 0 0 12px; }}
  .seo-block {{ background: #f9f9f0; border: 1px solid #e8e4c0; border-radius: 4px; padding: 12px 16px; margin-top: 16px; font-size: 12px; color: #666; }}
  .footer {{ background: #f9f9f9; padding: 20px 32px; font-size: 12px; color: #aaa; border-top: 1px solid #eee; text-align: center; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>IncastroPC - Articoli del giorno</h1>
    <p>{count} articoli pronti per WordPress - {date}</p>
  </div>
  <div class="content">{articles_html}</div>
  <div class="footer">Generato da IncastroPC News Bot - {date}</div>
</div>
</body>
</html>
"""

def parse_articles(raw_text):
    articles = []
    blocks = raw_text.split("---")
    for block in blocks:
        block = block.strip()
        if block and "<!-- ARTICOLO -->" in block:
            block = block.replace("<!-- ARTICOLO -->", "").strip()
            articles.append(block)
    return articles

def format_article_html(block, index):
    yoast_kp = yoast_meta = yoast_slug = ""
    cover_b64 = body_b64 = ""
    clean_lines = []

    for line in block.split("\n"):
        if line.startswith("YOAST_KEYPHRASE:"):
            yoast_kp = line.replace("YOAST_KEYPHRASE:", "").strip()
        elif line.startswith("YOAST_METADESC:"):
            yoast_meta = line.replace("YOAST_METADESC:", "").strip()
        elif line.startswith("YOAST_SLUG:"):
            yoast_slug = line.replace("YOAST_SLUG:", "").strip()
        elif line.startswith("COVER_IMAGE_B64:"):
            cover_b64 = line.replace("COVER_IMAGE_B64:", "").strip()
        elif line.startswith("BODY_IMAGE_B64:"):
            body_b64 = line.replace("BODY_IMAGE_B64:", "").strip()
        elif line.startswith("IMAGE_COVER:") or line.startswith("IMAGE_BODY:"):
            continue
        else:
            clean_lines.append(line)

    article_html = "\n".join(clean_lines).strip()

    # Immagine copertina
    cover_html = ""
    if cover_b64:
        cover_html = '<img src="data:image/jpeg;base64,' + cover_b64 + '" class="cover-img" alt="Copertina articolo ' + str(index) + '">'

    # Immagine interna dopo il secondo paragrafo
    if body_b64:
        body_img = '<img src="data:image/jpeg;base64,' + body_b64 + '" class="body-img" alt="Immagine articolo ' + str(index) + '">'
        parts = article_html.split("</p>", 2)
        if len(parts) >= 3:
            article_html = parts[0] + "</p>" + parts[1] + "</p>" + body_img + parts[2]

    # Blocco SEO
    seo_block = ""
    if yoast_kp or yoast_meta or yoast_slug:
        seo_block = (
            '<div class="seo-block">'
            '<strong>Yoast SEO</strong><br>'
            '<b>Keyphrase:</b> ' + yoast_kp + '<br>'
            '<b>Meta:</b> ' + yoast_meta + '<br>'
            '<b>Slug:</b> ' + yoast_slug +
            '</div>'
        )

    return (
        '<div class="article-block">'
        '<div class="article-header"><span class="article-num">Articolo ' + str(index) + '</span></div>'
        + cover_html +
        '<div class="article-body">' + article_html + seo_block + '</div>'
        '</div>'
    )

def send_digest(raw_text):
    today = datetime.date.today().strftime("%d %B %Y")
    article_blocks = parse_articles(raw_text)

    if not article_blocks:
        articles_html = "<pre>" + raw_text[:2000] + "</pre>"
        count = "0"
    else:
        articles_html = ""
        for i, block in enumerate(article_blocks, 1):
            articles_html += format_article_html(block, i)
        count = str(len(article_blocks))

    html_body = EMAIL_TEMPLATE.format(
        articles_html=articles_html,
        count=count,
        date=today
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "IncastroPC Articoli - " + today
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
    print("Email inviata a " + EMAIL_TO)
