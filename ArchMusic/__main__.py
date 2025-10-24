# ArchMusic/__main__.py - ParsMüzikBot Stabil Başlatıcı

import asyncio
import importlib
import sys
import os

from pyrogram import idle, filters
from pytgcalls.exceptions import NoActiveGroupCall

import config
from config import BANNED_USERS
from ArchMusic import LOGGER, app
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


# ✅ Otomatik Restart Sistemi
async def auto_restart(interval_minutes):
    while True:
        settings = await get_restart_settings()
        if not settings["enabled"]:
            break
        await asyncio.sleep(interval_minutes * 60)
        await restart_bot()


async def restart_bot():
    chats = await get_active_chats()
    for chat_id in chats:
        try:
            await app.send_message(chat_id, f"🔁 **{config.MUSIC_BOT_NAME} yeniden başlatılıyor...**")
        except:
            pass
    os.system(f"kill -9 {os.getpid()} && bash start")


@app.on_message(filters.command("autorestart") & filters.user(config.OWNER_ID))
async def auto_restart_cmd(_, message):
    if len(message.command) == 1:
        settings = await get_restart_settings()
        status = "✅ Açık" if settings["enabled"] else "❌ Kapalı"
        saat = settings["interval"] // 60
        return await message.reply_text(
            f"**🔄 Otomatik Yeniden Başlatma Durumu**\n"
            f"Durum: {status}\n"
            f"Saat Aralığı: {saat}\n\n"
            "**Kullanım:**\n"
            "`/autorestart on` - Aç\n"
            "`/autorestart off` - Kapat\n"
            "`/autorestart 6` - 6 saatte bir restart"
        )

    mode = message.command[1].lower()
    if mode == "on":
        await update_restart_settings(enabled=True)
        return await message.reply_text("✅ Otomatik restart **aktif edildi**.")
    elif mode == "off":
        await update_restart_settings(enabled=False)
        return await message.reply_text("❌ Otomatik restart **kapandı**.")
    else:
        try:
            saat = int(mode)
            await update_restart_settings(interval=saat * 60)
            return await message.reply_text(f"✅ Restart aralığı **{saat} saat** olarak ayarlandı.")
        except:
            return await message.reply_text("❌ Geçersiz format.")


# ✅ BOT BAŞLATMA
async def init():
    if not config.STRING1:
        LOGGER.error("❌ STRING1 girilmemiş! Assistant olmazsa bot çalışmaz.")
        return

    await app.start()

    # 🔧 Pluginleri güvenli yükle
    for module in ALL_MODULES:
        try:
            importlib.import_module(f"ArchMusic.plugins{module}")
            LOGGER.info(f"✔️ Plugin yüklendi: {module}")
        except Exception as e:
            LOGGER.error(f"❌ Plugin yüklenemedi ({module}): {e}")

    LOGGER.info("✅ Tüm pluginler yüklendi.")

    await ArchMusic.start()

    try:
        await ArchMusic.stream_call("http://docs.evostream.com/sample_content/assets/sintel1m720p.mp4")
    except NoActiveGroupCall:
        LOGGER.warning("⚠️ Log grubunun sesli sohbeti açık değil, devam ediyorum.")
    except:
        pass

    LOGGER.info(f"✅ {config.MUSIC_BOT_NAME} başarıyla başlatıldı!")
    settings = await get_restart_settings()

    if settings["enabled"]:
        global auto_restart_task
        auto_restart_task = asyncio.create_task(auto_restart(settings["interval"]))

    await idle()


if __name__ == "__main__":
    try:
        loop.run_until_complete(init())
    except KeyboardInterrupt:
        pass
    LOGGER.info("🛑 Bot kapatıldı.")
