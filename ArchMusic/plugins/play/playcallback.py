# -*- coding: utf-8 -*-
#
# ParsMuzikBot - Play Callback Controller
# Dark Steel System by @Kralderdo
# Güçlü hızlı müzik kontrol sistemi ⚡

from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup
from config import BANNED_USERS, OWNER_ID
from ArchMusic import app
from ArchMusic.core.call import ArchMusic
from ArchMusic.utils.database import is_muted, mute_off, mute_on
from ArchMusic.utils.inline.play import (
    stream_markup,
    track_markup,
    slider_markup,
    playlist_markup,
    livestream_markup,
)
from ArchMusic.utils.decorators.language import languageCB

# Güvenlik filtresi – Sadece OWNER + SUDO kullanabilir
def authorized(user_id):
    return user_id in OWNER_ID

# Sabit mesaj imzası
BOT_SIGNATURE = "⚙️ Powered by Prenses Müzik"

# ===============================================================
# ▶️ Play / Video Başlatma - Callback Kontrolleri
# ===============================================================
@app.on_callback_query(filters.regex("^MusicStream") & ~BANNED_USERS)
@languageCB
async def music_stream_cb(client, CallbackQuery: CallbackQuery, _):
    try:
        data = CallbackQuery.data.strip().split("|")
        videoid = data[0].replace("MusicStream ", "")
        user_id = int(data[1])
        mode = data[2]  # a = audio, v = video
        channel = True if data[3] == "c" else False
        fplay = True if data[4] == "f" else False
        chat_id = CallbackQuery.message.chat.id

        # ✅ Güvenlik kontrolü – Sadece OWNER + SUDO kullanabilir
        if not authorized(CallbackQuery.from_user.id):
            return await CallbackQuery.answer("⛔ Bu butonu kullanma yetkin yok!", show_alert=True)

        await CallbackQuery.answer("⏳ İşleniyor...")

        if mode == "v":
            streamtype = "video"
        else:
            streamtype = "audio"

        # Devam veya yeni çalma
        await ArchMusic.stream_call(videoid, chat_id, streamtype=streamtype, forceplay=fplay)

        await CallbackQuery.message.edit_text(
            f"🎶 **Parça Başlatıldı**\n"
            f"💠 **Mod:** {'🎬 Video' if mode=='v' else '🎧 Ses'}\n"
            f"{BOT_SIGNATURE}",
            reply_markup=InlineKeyboardMarkup(
                stream_markup(_, videoid, chat_id)
            ),
        )
    except Exception as e:
        return await CallbackQuery.message.reply_text(f"⚠️ Play Callback Hatası: `{e}`")

# ===============================================================
# 🎛 Müzik Kontrol Callback – Pause | Resume | Stop | Skip | Loop
# ===============================================================
@app.on_callback_query(filters.regex("^ADMIN") & ~BANNED_USERS)
@languageCB
async def admin_callbacks(client, CallbackQuery: CallbackQuery, _):
    try:
        command = CallbackQuery.data.split("|")
        action = command[0].replace("ADMIN ", "")
        chat_id = int(command[1])
        user = CallbackQuery.from_user.id

        # ✅ Güvenlik kontrolü
        if not authorized(user):
            return await CallbackQuery.answer("⛔ Bu paneli kullanamazsın!", show_alert=True)

        await CallbackQuery.answer()

        if action == "Pause":
            await ArchMusic.pause_stream(chat_id)
            return await CallbackQuery.message.reply_text("⏸ Müzik duraklatıldı!")

        elif action == "Resume":
            await ArchMusic.resume_stream(chat_id)
            return await CallbackQuery.message.reply_text("▶️ Müzik devam ediyor!")

        elif action == "Stop":
            await ArchMusic.stop_stream(chat_id)
            return await CallbackQuery.message.reply_text("⏹ Müzik kapatıldı!")

        elif action == "Skip":
            await ArchMusic.skip_stream(chat_id)
            return await CallbackQuery.message.reply_text("⏭ Sonraki şarkıya geçildi!")

        elif action == "Loop":
            await ArchMusic.loop_stream(chat_id)
            return await CallbackQuery.message.reply_text("🔁 Tekrar modu aktif!")

        else:
            return await CallbackQuery.answer("❗ Bilinmeyen işlem", show_alert=True)

    except Exception as e:
        return await CallbackQuery.message.reply_text(f"⚠️ Panel Hatası: {e}")


# ===============================================================
# 🔇 Ses Kontrol – Volume +10 | -10
# ===============================================================
@app.on_callback_query(filters.regex("^VOLUME") & ~BANNED_USERS)
async def volume_control(client, CallbackQuery: CallbackQuery):
    try:
        command = CallbackQuery.data.split("|")
        action = command[1]
        chat_id = int(command[2])

        if not authorized(CallbackQuery.from_user.id):
            return await CallbackQuery.answer("⛔ Yetkin yok!", show_alert=True)

        await CallbackQuery.answer()

        if action == "up":
            await ArchMusic.change_volume(chat_id, 10)
            return await CallbackQuery.message.reply_text("🔊 Ses artırıldı (+10)!")
        elif action == "down":
            await ArchMusic.change_volume(chat_id, -10)
            return await CallbackQuery.message.reply_text("🔉 Ses azaltıldı (-10)!")

    except Exception as e:
        return await CallbackQuery.message.reply_text(f"⚠️ Ses kontrol hatası: {e}")


print("[ParsMuzikBot] ✅ playcallback.py başarıyla yüklendi - Dark Steel buton sistemi aktif ⚙️")
