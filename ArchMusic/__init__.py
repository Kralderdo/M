# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2023 by ArchBots
# https://github.com/ArchBots/ArchMusic
#
# GPL-3.0 License
#

import logging
from ArchMusic.core.bot import ArchMusic
from ArchMusic.core.dir import dirr
from ArchMusic.core.userbot import Userbot
from ArchMusic.misc import dbb, heroku, sudo
from .platforms import *

# ✅ LOGGER FIX (Çökme sebebi burasıydı)
LOGGER = logging.getLogger("ParsMuzikBot")
logging.basicConfig(
    format="%(levelname)s | %(asctime)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    level=logging.INFO,
)

# 📁 Gerekli klasörleri hazırla
dirr()

# 🔧 Veritabanı başlat
dbb()

# ☁️ Heroku yapılandırması
heroku()

# 👑 Sudo kullanıcıları yükle
sudo()

# 🤖 Ana bot
app = ArchMusic()

# 🤝 Asistan (UserBot)
userbot = Userbot()

# 🎵 Platform API'leri başlat
YouTube = YouTubeAPI()
Carbon = CarbonAPI()
Spotify = SpotifyAPI()
Apple = AppleAPI()
Resso = RessoAPI()
SoundCloud = SoundAPI()
Telegram = TeleAPI()
