import os

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
EMAIL_FROM        = os.environ.get("EMAIL_FROM")
EMAIL_PASSWORD    = os.environ.get("EMAIL_PASSWORD")
EMAIL_TO          = os.environ.get("EMAIL_TO")

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
TOP_N     = 8

RSS_FEEDS = [
    ("GamingOnLinux",     "https://www.gamingonlinux.com/article_rss.php"),
    ("Phoronix",          "https://www.phoronix.com/rss.php"),
    ("Boiling Steam",     "https://boilingsteam.com/feed/"),
    ("r/linux_gaming",    "https://www.reddit.com/r/linux_gaming/.rss"),
    ("r/minipc",          "https://www.reddit.com/r/MiniPCs/.rss"),
    ("Tom's Hardware IT", "https://www.tomshw.it/rss_news.xml"),
    ("Everyeye",          "https://www.everyeye.it/rss_news.xml"),
    ("Spaziogames",       "https://www.spaziogames.it/feed/"),
    ("Multiplayer.it",    "https://www.multiplayer.it/rss/news.xml"),
    ("HWUpgrade",         "https://www.hwupgrade.it/rss/news.xml"),
    ("Tom's Hardware",    "https://www.tomshardware.com/feeds/all"),
    ("PC Gamer",          "https://www.pcgamer.com/rss/"),
    ("Rock Paper Shotgun","https://www.rockpapershotgun.com/feed"),
]

BOOST_KEYWORDS = [
    "linux", "proton", "wine", "steam deck", "steamos",
    "mini pc", "amd", "radeon", "ryzen", "igpu", "integrated graphics",
    "open source", "native", "vulkan", "gamescope",
    "cachy", "bazzite", "nobara", "arch",
    "instant gaming", "humble bundle", "fanatical", "offerta", "sconto",
]

PENALTY_KEYWORDS = [
    "playstation exclusive", "xbox exclusive", "nintendo switch 2",
    "mobile game", "nft", "blockchain", "metaverse",
]
