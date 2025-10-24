# ArchMusic/__main__.py

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
            await app.send_message(x, f"🔁 {config.MUSIC_BOT_NAME} yeniden başlatılıyor...")
        except:
            pass

    os.system(f"kill -9 {os.getpid()} && bash start")


@app.on_message(filters.command("autorestart") & filters.user(config.OWNER_ID))
async def auto_restart_command(_, message):
    if len(message.command) == 1:
        settings = await get_restart_settings()
        status = "✅ Açık" if settings["enabled"] else "❌ Kapalı"
        hours = settings["interval"] // 60
        return await message.reply_text(
            f"🔧 Auto-Restart: {status}\n⏰ Süre: {hours} saat"
        )


async def init():
    await app.start()

    # ✅ PLUGIN YÜKLEME HATASI BURADA ÇÖZÜLDÜ
    for all_module in ALL_MODULES:
        try:
            importlib.import_module(f"ArchMusic.plugins.{all_module}")
            LOGGER.info(f"✅ Plugin yüklendi: {all_module}")
        except Exception as e:
            LOGGER.error(f"❌ Plugin yüklenemedi ({all_module}): {e}")

    await ArchMusic.start()

    try:
        await ArchMusic.stream_call("http://docs.evostream.com/sample_content/assets/sintel1m720p.mp4")
    except:
        pass

    LOGGER.info(f"✅ {config.MUSIC_BOT_NAME} başarıyla başlatıldı!")
    await idle()


if __name__ == "__main__":
    loop.run_until_complete(init())
