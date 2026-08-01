import os

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
EMAIL_FROM        = os.environ.get("EMAIL_FROM")
EMAIL_PASSWORD    = os.environ.get("EMAIL_PASSWORD")
EMAIL_TO          = os.environ.get("EMAIL_TO")

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
TOP_N     = 5

RSS_FEEDS = [
    # Linux gaming - news giornaliere
    ("GamingOnLinux",     "https://www.gamingonlinux.com/article_rss.php"),
    ("Phoronix",          "https://www.phoronix.com/rss.php"),
    ("Boiling Steam",     "https://boilingsteam.com/feed/"),
    # Community
    ("r/linux_gaming",    "https://www.reddit.com/r/linux_gaming/.rss"),
    ("r/linux",           "https://www.reddit.com/r/linux/.rss"),
    ("r/SteamDeck",       "https://www.reddit.com/r/SteamDeck/.rss"),
    ("r/minipc",          "https://www.reddit.com/r/MiniPCs/.rss"),
    # Italiani
    ("Tom's Hardware IT", "https://www.tomshw.it/rss_news.xml"),
    ("Everyeye",          "https://www.everyeye.it/rss_news.xml"),
    ("Multiplayer.it",    "https://www.multiplayer.it/rss/news.xml"),
    # Internazionale
    ("Tom's Hardware",    "https://www.tomshardware.com/feeds/all"),
    ("PC Gamer",          "https://www.pcgamer.com/rss/"),
    ("Rock Paper Shotgun","https://www.rockpapershotgun.com/feed"),
]

# Boost forte per notizie fresche e rilevanti
BOOST_KEYWORDS = [
    # Linux/Proton news
    "linux", "proton", "wine", "steam deck", "steamos",
    "proton ge", "wine ge", "lutris", "heroic",
    # Hardware IncastroPC
    "mini pc", "amd", "radeon", "ryzen", "igpu", "integrated graphics",
    "rdna", "apu", "vega", "780m", "890m",
    "intel arc", "xe graphics",
    # Attualità
    "released", "announced", "update", "launch", "now available",
    "just released", "new version", "patch", "fix", "support added",
    "rilasciato", "annunciato", "aggiornamento", "supporto",
    # Open source
    "open source", "native", "vulkan", "gamescope", "wayland",
    "mesa", "kernel", "driver",
    # Distro gaming
    "cachyos", "bazzite", "nobara", "arch", "fedora",
    # Offerte
    "humble bundle", "fanatical", "offerta", "sconto", "free",
]

# Penalità forte per contenuti evergreen e fuori tema
PENALTY_KEYWORDS = [
    # Guide generiche
    "how to", "guide", "tutorial", "best of", "top 10",
    "should you", "vs", "comparison", "review", "hands on",
    "come fare", "guida", "confronto", "recensione",
    # Fuori tema
    "playstation", "xbox exclusive", "nintendo",
    "mobile game", "ios", "android game",
    "nft", "blockchain", "metaverse", "crypto",
    "dash cam", "dashcam", "telecamera auto",
    "smartphone", "iphone", "samsung",
    "tablet", "smart tv", "alexa",
    "offerta amazon", "coupon",
]
