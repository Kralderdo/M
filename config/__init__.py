import os
from dotenv import load_dotenv

if os.path.exists(".env"):
    load_dotenv(".env")

# Temel Telegram API Bilgileri
API_ID = int(os.getenv("API_ID", ""))
API_HASH = os.getenv("API_HASH", "")

# Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Bot İsmi
MUSIC_BOT_NAME = os.getenv("MUSIC_BOT_NAME", "Pars Müzik Bot")

# Owner ID (Sahip)
OWNER_ID = int(os.getenv("OWNER_ID", "6366762649"))

# Log Grubu
LOG_GROUP_ID = int(os.getenv("LOG_GROUP_ID", "-1002970992169"))

# Destek Linkleri
SUPPORT_CHANNEL = os.getenv("SUPPORT_CHANNEL", "https://t.me/Los_Angaras_06")
SUPPORT_GROUP = os.getenv("SUPPORT_GROUP", "https://t.me/Pars_Sohbet_TR")

# MongoDB
MONGO_DB_URI = os.getenv("MONGO_DB_URI", "")

# Spotify API (Opsiyonel)
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")

# Broadcast & Komut Yetkilileri
SUDO_USERS = list(map(int, os.getenv("SUDO_USERS", "6366762649").split()))

# String Session (Assistant Kullanıcı)
STRING1 = os.getenv("STRING1", "")
STRING2 = os.getenv("STRING2", "")
STRING3 = os.getenv("STRING3", "")
STRING4 = os.getenv("STRING4", "")
STRING5 = os.getenv("STRING5", "")

# Log Dosyası (Önemli hata buradan geliyordu ✅)
LOG_FILE_NAME = "pars_music_logs.txt"

# Otomatik Temizlik
AUTO_DOWNLOADS_CLEAR = os.getenv("AUTO_DOWNLOADS_CLEAR", "True")

# Py-TgCalls Seçenekleri
PRIVATE_BOT_MODE = os.getenv("PRIVATE_BOT_MODE", "False")
