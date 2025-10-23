import re
import sys
from os import getenv
from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()

# Get it from my.telegram.org
API_ID = int(getenv("API_ID", ""))
API_HASH = getenv("API_HASH", "")

# Get it from @Botfather in Telegram.
BOT_TOKEN = getenv("BOT_TOKEN", "")

# Database to save your chats and stats.
MONGO_DB_URI = getenv("MONGO_DB_URI", "")

# Custom max audio(music) duration for voice chat. Default to 180 mins.
DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", "180"))

# Bot introduction effects
AYU = ["💞", "🦋", "🔍", "🧪", "⚡️", "🔥", "🎩", "🌈", "🍷", "🥂", "🥃", "🕊️", "🪄", "💌", "🧨"]

# Stickers
STICKERS = [
    "CAACAgUAAx0Cd6nKUAACASBl_rnalOle6g7qS-ry-aZ1ZpVEnwACgg8AAizLEFfI5wfykoCR4h4E",
    "CAACAgUAAx0Cd6nKUAACATJl_rsEJOsaaPSYGhU7bo7iEwL8AAPMDgACu2PYV8Vb8aT4_HUPHgQ"
]

# Song download duration limit
SONG_DOWNLOAD_DURATION = int(getenv("SONG_DOWNLOAD_DURATION_LIMIT", "180"))

# Private log group ID
LOG_GROUP_ID = int(getenv("LOG_GROUP_ID", ""))

# A name for the Music bot
MUSIC_BOT_NAME = getenv("MUSIC_BOT_NAME", "Kumsal Muzik")

# Owner ID (your user ID)
OWNER_ID = list(map(int, getenv("OWNER_ID", "").split()))

# Heroku configs
HEROKU_API_KEY = getenv("HEROKU_API_KEY")
HEROKU_APP_NAME = getenv("HEROKU_APP_NAME")

# Upstream repo (for updates)
UPSTREAM_REPO = getenv("UPSTREAM_REPO", "https://github.com/zuchzub/M")
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "main")

# Git token if your repo is private
GIT_TOKEN = getenv("GIT_TOKEN", "")

# Support links
SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "")
SUPPORT_GROUP = getenv("SUPPORT_GROUP", None)

# Auto leave assistant
AUTO_LEAVING_ASSISTANT = getenv("AUTO_LEAVING_ASSISTANT", "false")
AUTO_LEAVE_ASSISTANT_TIME = int(getenv("ASSISTANT_LEAVE_TIME", "5400"))

# Auto suggestions
AUTO_SUGGESTION_TIME = int(getenv("AUTO_SUGGESTION_TIME", "5400"))
AUTO_SUGGESTION_MODE = getenv("AUTO_SUGGESTION_MODE", None)

# Auto clear downloads after play
AUTO_DOWNLOADS_CLEAR = getenv("AUTO_DOWNLOADS_CLEAR", None)

# Private bot mode
PRIVATE_BOT_MODE = getenv("PRIVATE_BOT_MODE", None)

# Download sleep settings
YOUTUBE_DOWNLOAD_EDIT_SLEEP = int(getenv("YOUTUBE_EDIT_SLEEP", "3"))
TELEGRAM_DOWNLOAD_EDIT_SLEEP = int(getenv("TELEGRAM_EDIT_SLEEP", "5"))

# Github repo link
GITHUB_REPO = getenv("GITHUB_REPO", "https://github.com/zuchzub/M")

# Spotify API configs
SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", "2041df9cbcd142cba804578a2cf85939")
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", "80ffd296320e49299830e80b11e3bf73")

# ✅ YouTube API Key (EKLENDİ)
YOUTUBE_API_KEY = "AIzaSyBWEUJjXpdrWP9lNdkhuiynVjyqnIzd-So"

# Video stream limit
VIDEO_STREAM_LIMIT = int(getenv("VIDEO_STREAM_LIMIT", "10"))

# Playlists limit
SERVER_PLAYLIST_LIMIT = int(getenv("SERVER_PLAYLIST_LIMIT", "100"))
PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", "50"))

# Clean mode
CLEANMODE_DELETE_MINS = int(getenv("CLEANMODE_MINS", "5000000"))

# Telegram File Size Limits
TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", "104857600"))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", "1073741824"))

# Auto setup bot commands
SET_CMDS = getenv("SET_CMDS", False)

# Pyrogram String Sessions
STRING1 = getenv("STRING_SESSION", "")
STRING2 = getenv("STRING_SESSION2", "")
STRING3 = getenv("STRING_SESSION3", "")
STRING4 = getenv("STRING_SESSION4", None)
STRING5 = getenv("STRING_SESSION5", None)

### DONT TOUCH or EDIT codes after this line

BANNED_USERS = filters.user()
YTDOWNLOADER = 1
LOG = 2
LOG_FILE_NAME = "Worexis.txt"

adminlist = {}
lyrical = {}
chatstats = {}
userstats = {}
clean = {}
autoclean = []

# Images
START_IMG_URL = getenv(
     "START_IMG_URL", 
     "https://ibb.co/0jsDgHSj",
)

PING_IMG_URL = getenv(
    "PING_IMG_URL",
    "https://ibb.co/0jsDgHSj",
)

PLAYLIST_IMG_URL = getenv(
    "PLAYLIST_IMG_URL",
    "https://ibb.co/0jsDgHSj",
)

GLOBAL_IMG_URL = getenv(
    "GLOBAL_IMG_URL",
    "https://pbs.twimg.com/media/GlYNUMFWEAA4jEK?format=jpg&name=small",
)

STATS_IMG_URL = getenv(
    "STATS_IMG_URL",
    "https://pbs.twimg.com/media/GlYNUMFWEAA4jEK?format=jpg&name=small",
)

TELEGRAM_AUDIO_URL = getenv(
    "TELEGRAM_AUDIO_URL",
    "https://pbs.twimg.com/media/GlYNUMFWEAA4jEK?format=jpg&name=small",
)

TELEGRAM_VIDEO_URL = getenv(
    "TELEGRAM_VIDEO_URL",
    "https://pbs.twimg.com/media/GlYNUMFWEAA4jEK?format=jpg&name=small",
)

STREAM_IMG_URL = getenv(
    "STREAM_IMG_URL",
    "https://pbs.twimg.com/media/GlYNUMFWEAA4jEK?format=jpg&name=small",
)

SOUNCLOUD_IMG_URL = getenv(
    "SOUNCLOUD_IMG_URL",
    "https://pbs.twimg.com/media/GlYNUMFWEAA4jEK?format=jpg&name=small",
)

YOUTUBE_IMG_URL = getenv(
    "YOUTUBE_IMG_URL",
    "https://pbs.twimg.com/media/GlYNUMFWEAA4jEK?format=jpg&name=small",
)

SPOTIFY_ARTIST_IMG_URL = getenv(
    "SPOTIFY_ARTIST_IMG_URL",
    "https://pbs.twimg.com/media/GlYNUMFWEAA4jEK?format=jpg&name=small",
)

SPOTIFY_ALBUM_IMG_URL = getenv(
    "SPOTIFY_ALBUM_IMG_URL",
    "https://pbs.twimg.com/media/GlYNUMFWEAA4jEK?format=jpg&name=small",
)

SPOTIFY_PLAYLIST_IMG_URL = getenv(
    "SPOTIFY_PLAYLIST_IMG_URL",
    "https://pbs.twimg.com/media/GlYNUMFWEAA4jEK?format=jpg&name=small",
)

def time_to_seconds(time):
    stringt = str(time)
    return sum(
        int(x) * 60**i
        for i, x in enumerate(reversed(stringt.split(":")))
    )

DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))
SONG_DOWNLOAD_DURATION_LIMIT = int(
    time_to_seconds(f"{SONG_DOWNLOAD_DURATION}:00")
)

if SUPPORT_CHANNEL:
    if not re.match("(?:http|https)://", SUPPORT_CHANNEL):
        print("[ERROR] - SUPPORT_CHANNEL url must start with https://")
        sys.exit()

if SUPPORT_GROUP:
    if not re.match("(?:http|https)://", SUPPORT_GROUP):
        print("[ERROR] - SUPPORT_GROUP url must start with https://")
        sys.exit()

if UPSTREAM_REPO:
    if not re.match("(?:http|https)://", UPSTREAM_REPO):
        print("[ERROR] - UPSTREAM_REPO url must start with https://")
        sys.exit()

if GITHUB_REPO:
    if not re.match("(?:http|https)://", GITHUB_REPO):
        print("[ERROR] - GITHUB_REPO url must start with https://")
        sys.exit()

if PING_IMG_URL:
    if PING_IMG_URL != "assets/Ping.jpeg":
        if not re.match("(?:http|https)://", PING_IMG_URL):
            print("[ERROR] - PING_IMG_URL must start with https://")
            sys.exit()

if not MUSIC_BOT_NAME.isascii():
    print("[ERROR] - MUSIC_BOT_NAME must be ASCII characters only!")
    sys.exit()
