import os

# ─── AI ───────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
AI_PROVIDER       = os.environ.get("AI_PROVIDER", "anthropic")  # anthropic | local | hybrid
OLLAMA_MODEL      = os.environ.get("OLLAMA_MODEL", "mistral:7b")
OLLAMA_URL        = os.environ.get("OLLAMA_URL", "http://localhost:11434")

# ─── Email ────────────────────────────────────────────────
SMTP_HOST      = "smtp.gmail.com"
SMTP_PORT      = 587
EMAIL_FROM     = os.environ.get("EMAIL_FROM", "")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "")
EMAIL_TO       = os.environ.get("EMAIL_TO", "")

# ─── WordPress ────────────────────────────────────────────
WP_URL      = os.environ.get("WP_URL", "").rstrip("/")
WP_USERNAME = os.environ.get("WP_USERNAME", "")
WP_PASSWORD = os.environ.get("WP_PASSWORD", "")
WP_STATUS   = os.environ.get("WORDPRESS_STATUS", "draft")  # draft | publish
WP_TIMEOUT  = int(os.environ.get("WP_TIMEOUT", "30"))

# ─── Pipeline ─────────────────────────────────────────────
TOP_N              = int(os.environ.get("TOP_N", "5"))
MIN_SCORE          = int(os.environ.get("MIN_SCORE", "60"))
HOURS_BACK         = int(os.environ.get("HOURS_BACK", "12"))
IN_ARTICLE_IMAGES  = int(os.environ.get("IN_ARTICLE_IMAGES", "2"))
AI_PROVIDER        = os.environ.get("AI_PROVIDER", "anthropic")

# ─── Immagini ─────────────────────────────────────────────
IMAGE_PROVIDER = os.environ.get("IMAGE_PROVIDER", "pollinations")  # pollinations | local | none
IMAGE_WIDTH    = int(os.environ.get("IMAGE_WIDTH", "1200"))
IMAGE_HEIGHT   = int(os.environ.get("IMAGE_HEIGHT", "630"))

# ─── Social ───────────────────────────────────────────────
SOCIAL_ENABLED  = os.environ.get("SOCIAL_ENABLED", "false").lower() == "true"
TELEGRAM_TOKEN  = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT   = os.environ.get("TELEGRAM_CHAT", "")

# ─── Feed RSS ─────────────────────────────────────────────
RSS_FEEDS = [
    ("GamingOnLinux",     "https://www.gamingonlinux.com/article_rss.php"),
    ("Phoronix",          "https://www.phoronix.com/rss.php"),
    ("Boiling Steam",     "https://boilingsteam.com/feed/"),
    ("r/linux_gaming",    "https://www.reddit.com/r/linux_gaming/.rss"),
    ("r/linux",           "https://www.reddit.com/r/linux/.rss"),
    ("r/SteamDeck",       "https://www.reddit.com/r/SteamDeck/.rss"),
    ("r/minipc",          "https://www.reddit.com/r/MiniPCs/.rss"),
    ("Tom's Hardware IT", "https://www.tomshw.it/rss_news.xml"),
    ("Everyeye",          "https://www.everyeye.it/rss_news.xml"),
    ("Multiplayer.it",    "https://www.multiplayer.it/rss/news.xml"),
    ("Tom's Hardware",    "https://www.tomshardware.com/feeds/all"),
    ("PC Gamer",          "https://www.pcgamer.com/rss/"),
    ("Rock Paper Shotgun","https://www.rockpapershotgun.com/feed"),
]

# ─── Keywords ─────────────────────────────────────────────
BOOST_KEYWORDS = [
    "linux", "proton", "wine", "steam deck", "steamos",
    "proton ge", "wine ge", "lutris", "heroic",
    "mini pc", "amd", "radeon", "ryzen", "igpu", "integrated graphics",
    "rdna", "apu", "vega", "780m", "890m",
    "intel arc", "xe graphics",
    "released", "announced", "update", "launch", "now available",
    "just released", "new version", "patch", "fix", "support added",
    "rilasciato", "annunciato", "aggiornamento", "supporto",
    "open source", "native", "vulkan", "gamescope", "wayland",
    "mesa", "kernel", "driver",
    "cachyos", "bazzite", "nobara", "arch", "fedora",
    "humble bundle", "fanatical", "offerta", "sconto", "free",
]

PENALTY_KEYWORDS = [
    "how to", "guide", "tutorial", "best of", "top 10",
    "should you", "vs", "comparison", "review", "hands on",
    "come fare", "guida", "confronto", "recensione",
    "playstation", "xbox exclusive", "nintendo",
    "mobile game", "ios", "android game",
    "nft", "blockchain", "metaverse", "crypto",
    "dash cam", "dashcam", "telecamera auto",
    "smartphone", "iphone", "samsung",
    "tablet", "smart tv", "alexa",
    "offerta amazon", "coupon",
    "aspirapolvere", "lavapavimenti", "robot pulizia",
]
