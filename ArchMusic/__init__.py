# -*- coding: utf-8 -*-

import logging

# ✅ LOGGER FIX
LOGGER = logging.getLogger("ParsMuzikBot")
logging.basicConfig(
    format="%(levelname)s | %(asctime)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    level=logging.INFO,
)

# ✅ Önce bu importlar gelmeli (çünkü bunlar bağımsız)
from ArchMusic.core.dir import dirr
from ArchMusic.misc import dbb, heroku, sudo

# ✅ Sistem dosyalarını hazırla
dirr()
dbb()
heroku()
sudo()

# ✅ Sonra botu import ediyoruz (circular import olmaması için BURADA OLMALI)
from ArchMusic.core.bot import ArchMusic
from ArchMusic.core.userbot import Userbot

# ✅ Botları başlat
app = ArchMusic()
userbot = Userbot()

# ✅ Platform API'leri en sona alıyoruz (çünkü botlar hazır olmalı)
from .platforms import (
    YouTubeAPI,
    CarbonAPI,
    SpotifyAPI,
    AppleAPI,
    RessoAPI,
    SoundAPI,
    TeleAPI,
)

YouTube = YouTubeAPI()
Carbon = CarbonAPI()
Spotify = SpotifyAPI()
Apple = AppleAPI()
Resso = RessoAPI()
SoundCloud = SoundAPI()
Telegram = TeleAPI()
