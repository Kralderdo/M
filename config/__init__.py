import os
from dotenv import load_dotenv

load_dotenv()

# Temel Bot Ayarları
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Sahipler
OWNER_ID = int(os.getenv("OWNER_ID", "6366762649"))
SUDO_USERS = list(map(int, os.getenv("SUDO_USERS", "6366762649").split()))

# Asistan STRING
STRING1 = os.getenv("STRING1")

# Log ve Destek
LOG_GROUP_ID = int(os.getenv("LOG_GROUP_ID", "-1002970992169"))
SUPPORT_CHANNEL = os.getenv("SUPPORT_CHANNEL", "https://t.me/Los_Angaras_06")
SUPPORT_GROUP = os.getenv("SUPPORT_GROUP", "https://t.me/Pars_Sohbet_TR")

# Bot adı
MUSIC_BOT_NAME = os.getenv("MUSIC_BOT_NAME", "Pars Müzik Bot")
