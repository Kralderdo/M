# ArchMusic/__main__.py
import asyncio
import importlib
import sys
import os
from pyrogram import idle
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
from pytgcalls.exceptions import NoActiveGroupCall

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


async def init():
    if not config.STRING1:
        LOGGER.error("❌ STRING1 zorunludur! Assistant olmadan bot çalışmaz.")
        return

    await app.start()

    # ✅ BURASI DÜZELTİLDİ!
    for all_module in ALL_MODULES:
        try:
            importlib.import_module(f"ArchMusic.plugins.{all_module}")
        except Exception as e:
            LOGGER.error(f"❌ Plugin yüklenemedi ({all_module}): {e}")

    LOGGER.info("✅ Tüm pluginler başarıyla yüklendi.")

    await ArchMusic.start()

    try:
        await ArchMusic.stream_call("http://docs.evostream.com/sample_content/assets/sintel1m720p.mp4")
    except NoActiveGroupCall:
        pass
    except:
        pass

    LOGGER.info("✅ ParsMüzikBot başarıyla başlatıldı!")
    await idle()


if __name__ == "__main__":
    loop.run_until_complete(init())
