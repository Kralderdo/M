# -*- coding: utf-8 -*-

import logging

# ✅ Logger Ayarı
LOGGER = logging.getLogger("ParsMuzikBot")
logging.basicConfig(
    format="%(levelname)s | %(asctime)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    level=logging.INFO,
)

# ✅ ÖNCE temel bağımlılıkları yükle (çünkü döngüsel import olmaması gerekiyor)
from ArchMusic.core.dir import dirr
from ArchMusic.misc import dbb, heroku, sudo

# ✅ Sistem Hazırlığı
dirr()         # klasör kontrol
dbb()          # db oluştur
heroku()       # heroku config
sudo()         # sudo kullanıcıları yükle

# ✅ Botları import ediyoruz (circular import engellemek için BURADA)
from ArchMusic.core.bot import ArchMusic
from ArchMusic.core.userbot import Userbot

# ✅ Bot Client örnekleri
app = ArchMusic()
userbot = Userbot()

# ✅ Platform API'leri (En son yüklenecek)
from ArchMusic.platforms import (
    YouTubeAPI,
    CarbonAPI,
    SpotifyAPI,
    AppleAPI,
    RessoAPI,
    SoundAPI,
    TeleAPI,
)

# ✅ Kullanım için hazır API objeleri
YouTube = YouTubeAPI()
Carbon = CarbonAPI()
Spotify = SpotifyAPI()
Apple = AppleAPI()
Resso = RessoAPI()
SoundCloud = SoundAPI()
Telegram = TeleAPI()
