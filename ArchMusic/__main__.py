import asyncio
import importlib
import sys
import os

from pyrogram import idle, filters
from pytgcalls.exceptions import NoActiveGroupCall

import config
from config import BANNED_USERS
from ArchMusic import LOGGER, app, userbot
from ArchMusic.core.call import ArchMusic
from ArchMusic.plugins import ALL_MODULES
from ArchMusic.utils.database import (
     get_banned_users, 
     get_gbanned, 
     get_active_chats,
     get_restart_settings, 
     update_restart_settings
)

loop = asyncio.get_event_loop_policy().get_event_loop()
auto_restart_task = None

async def auto_restart(interval_minutes):
    while True:
        settings = await get_restart_settings()
        if not settings["enabled"]:
            break
        await asyncio.sleep(interval_minutes * 60)
        await restart_bot()

async def restart_bot():
    served_chats = await get_active_chats()
    for x in served_chats:
        try:
            await app.send_message(
                x,
                f"**{config.MUSIC_BOT_NAME} kendini yeniden başlattı. Sorun için özür dileriz.\n\n10-15 saniye sonra yeniden müzik çalmaya başlayabilirsiniz.**",
            )
        except:
            pass
    try:
        await app.send_message(
            config.LOG_GROUP_ID,
            f"**{config.MUSIC_BOT_NAME} kendini otomatik olarak yeniden başlatıyor.**",
        )
    except:
        pass
    os.system(f"kill -9 {os.getpid()} && bash start")

@app.on_message(filters.command("autorestart") & filters.user(config.OWNER_ID))
async def auto_restart_command(_, message):
    if len(message.command) == 1:
        settings = await get_restart_settings()
        status = "✅ Açık" if settings["enabled"] else "❌ Kapalı"
        interval_hours = settings["interval"] // 60
        await message.reply_text(
            f"🔄 Otomatik Yeniden Başlatma: {status}\n"
            f"⏰ Yeniden Başlatma Aralığı: {interval_hours} saat\n\n"
            "Kullanım:\n"
            "`/autorestart on` - Aç\n"
            "`/autorestart off` - Kapat\n"
            "`/autorestart [saat]` - Saat ayarla`"
        )
        return

async def init():
    if not any([config.STRING1, config.STRING2, config.STRING3, config.STRING4, config.STRING5]):
        LOGGER.error("❌ Hiçbir asistan STRING SESSION eklenmemiş!")
        return

    if not config.SPOTIFY_CLIENT_ID and not config.SPOTIFY_CLIENT_SECRET:
        LOGGER.warning("⚠️ Spotify API bilgileri eksik! Spotify çalışmayacak.")

    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except:
        pass

    await app.start()

    for all_module in ALL_MODULES:
        importlib.import_module("ArchMusic.plugins" + all_module)

    LOGGER.info("✅ Modüller başarıyla yüklendi.")

    await userbot.start()
    await ArchMusic.start()

    try:
        await ArchMusic.stream_call(
            "http://docs.evostream.com/sample_content/assets/sintel1m720p.mp4"
        )
    except NoActiveGroupCall:
        LOGGER.error("⚠️ Log grubunda aktif sesli sohbet yok!")
        sys.exit()
    except:
        pass

    # ✅ Hatalı satır kaldırıldı
    # await ArchMusic.decorators()

    LOGGER.info("✅ ParsMüzikBot başarıyla başlatıldı!")

    settings = await get_restart_settings()
    if settings["enabled"]:
        global auto_restart_task
        auto_restart_task = asyncio.create_task(auto_restart(settings["interval"]))

    await idle()


if __name__ == "__main__":
    loop.run_until_complete(init())
    LOGGER.info("🛑 ParsMüzikBot durduruldu. Görüşmek üzere!")
