# ArchMusic/__main__.py

import asyncio
import importlib
import sys
import os

from pyrogram import idle, filters

import config
from config import BANNED_USERS
from ArchMusic import LOGGER, app  # userbot kaldırıldı çünkü tek assistant var
from ArchMusic.core.call import ArchMusic  # Tek-asistan call.py kullanıyoruz
from ArchMusic.plugins import ALL_MODULES
from ArchMusic.utils.database import (
     get_banned_users,
     get_gbanned,
     get_active_chats,
     get_restart_settings,
     update_restart_settings
)
from pytgcalls.exceptions import NoActiveGroupCall

loop = asyncio.get_event_loop_policy().get_event_loop()
auto_restart_task = None


# ✅ Auto restart sistemi aktif
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
                f"**{config.MUSIC_BOT_NAME} kendini yeniden başlattı.**\n10-15 saniye sonra devam edecek..."
            )
        except:
            pass
    try:
        await app.send_message(
            config.LOG_GROUP_ID,
            f"🔁 {config.MUSIC_BOT_NAME} otomatik yeniden başlatılıyor..."
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
        return await message.reply_text(
            f"🔄 **Otomatik Yeniden Başlatma**\n"
            f"Durum: {status}\n"
            f"Saat Aralığı: {interval_hours} saat\n\n"
            "**Kullanım:**\n"
            "`/autorestart on` - Aç\n"
            "`/autorestart off` - Kapat\n"
            "`/autorestart 6` - 6 saatte bir restart"
        )


async def init():
    if not config.STRING1:
        LOGGER.error("❌ STRING1 zorunludur! Assistant bağlanamaz.")
        return

    if not config.SPOTIFY_CLIENT_ID and not config.SPOTIFY_CLIENT_SECRET:
        LOGGER.warning("⚠️ Spotify API yok, sorun değil devam ediyorum.")

    try:
        for user_id in await get_gbanned():
            BANNED_USERS.add(user_id)
        for user_id in await get_banned_users():
            BANNED_USERS.add(user_id)
    except:
        pass

    await app.start()

    # ✅ Plugin yükleyici düzeltildi
    for all_module in ALL_MODULES:
        importlib.import_module(f"ArchMusic.plugins.{all_module}")

    LOGGER.info("✅ Modüller başarıyla yüklendi.")

    await ArchMusic.start()  # ✅ tek asistan call.py start çağrısı

    try:
        await ArchMusic.stream_call(
            "http://docs.evostream.com/sample_content/assets/sintel1m720p.mp4"
        )
    except NoActiveGroupCall:
        LOGGER.warning("⚠️ Log grubu sesli sohbete açık değil, devam ediyorum.")
    except:
        pass

    LOGGER.info("✅ ParsMüzikBot başarıyla başlatıldı!")

    settings = await get_restart_settings()
    if settings["enabled"]:
        global auto_restart_task
        auto_restart_task = asyncio.create_task(auto_restart(settings["interval"]))

    await idle()


if __name__ == "__main__":
    loop.run_until_complete(init())
    LOGGER.info("🛑 ParsMüzikBot durduruldu.")
