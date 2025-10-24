# -*- coding: utf-8 -*-
import os
import re
import sys
from os import getenv
from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()

# =========================
# Telegram API
# =========================
API_ID = int(getenv("API_ID", "0"))
API_HASH = getenv("API_HASH", "")

# Bot Token
BOT_TOKEN = getenv("BOT_TOKEN", "")

# MongoDB
MONGO_DB_URI = getenv("MONGO_DB_URI", "")

# =========================
# Bot Zaman Limitleri
# =========================
DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", "180"))  # dakika
SONG_DOWNLOAD_DURATION = int(getenv("SONG_DOWNLOAD_DURATION_LIMIT", "180"))

# =========================
# Sahip ve Log Grubu
# =========================
OWNER_ID = list(map(int, getenv("OWNER_ID", "6366762649").split()))
LOG_GROUP_ID = int(getenv("LOG_GROUP_ID", "-1002970992169"))

# =========================
# Bot Adı
# =========================
MUSIC_BOT_NAME = getenv("MUSIC_BOT_NAME", "ParsMuzikBot")

# =========================
# Heroku Ayarları
# =========================
HEROKU_APP_NAME = getenv("HEROKU_APP_NAME", "")
HEROKU_API_KEY = getenv("HEROKU_API_KEY", "")

# =========================
# güncelleme repo
# =========================
UPSTREAM_REPO = getenv("UPSTREAM_REPO", "https://github.com/Kralderdo/M")
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "main")
GIT_TOKEN = getenv("GIT_TOKEN", "")

# =========================
# Destek Linkleri
# =========================
SUPPORT_CHANNEL = ""
SUPPORT_GROUP = "https://t.me/Pars_Sohbet_TR"

# =========================
# YouTube API
# =========================
YOUTUBE_API_KEY = getenv("YOUTUBE_API_KEY", "AIzaSyBWEUJjXpdrWP9lNdkhuiynVjyqnIzd-So")

# =========================
# Spotify API
# =========================
SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", "")

# =========================
# Görseller
# =========================
START_IMG_URL = "https://telegra.ph/file/cc8c09f1a7de0b191c2b7.jpg"
PING_IMG_URL = "https://telegra.ph/file/cc8c09f1a7de0b191c2b7.jpg"
PLAYLIST_IMG_URL = "https://telegra.ph/file/cc8c09f1a7de0b191c2b7.jpg"

# =========================
# Log Dosyası Hatası Fix
# =========================
LOG_FILE_NAME = "ParsMuzik.log"

# =========================
# Gereken Diğer Sabitler
# =========================
BANNED_USERS = filters.user()
YTDOWNLOADER = 1

def time_to_seconds(time):
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(time.split(":"))))

DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))
SONG_DOWNLOAD_DURATION_LIMIT = int(time_to_seconds(f"{SONG_DOWNLOAD_DURATION}:00"))

# ASCII Bot Adı Kontrolü
if not MUSIC_BOT_NAME.isascii():
    print("[ERROR] - Bot adı ASCII olmalı! Türkçe karakter kullanma.")
    sys.exit()
