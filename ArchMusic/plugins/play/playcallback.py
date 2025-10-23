# -*- coding: utf-8 -*-
#
# ParsMuzikBot - Play Callback Controller
# Düzenleme: @Kralderdo
# ----------------------------------------------

from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup
from config import BANNED_USERS
from strings import get_command
from ArchMusic import app
from ArchMusic.core.call import ArchMusic
from ArchMusic.utils.database import is_muted, mute_off, mute_on
from ArchMusic.utils.inline.play import (
    stream_markup,
    audio_markup,
    video_markup,
)
from ArchMusic.utils.decorators.language import languageCB

# Geri dönüş callback butonlarının prefixi
PLAY_CALLBACK = "play_callback"

# ===============================================================
# ▶️ MÜZİĞİ VEYA VİDEOYU ÇAL / PLAY BUTTON KONTROLÜ
# ===============================================================
@app.on_callback_query(filters.regex("play"))
@languageCB
async def play_callbacks(client, CallbackQuery: CallbackQuery, _):
    try:
        command = CallbackQuery.data.split("|")
        action = command[1]
        video = True if command[2] == "v" else False
        channel = True if command[3] == "c" else False
        fplay = True if command[4] == "f" else False
        user_id = CallbackQuery.from_user.id
        chat_id = CallbackQuery.message.chat.id

        if action == "stream":
            await CallbackQuery.answer()
            await ArchMusic.resume_stream(chat_id)
            return await CallbackQuery.message.reply_text("▶️ Devam ettirildi!")

        elif action == "pause":
            await CallbackQuery.answer()
            await ArchMusic.pause_stream(chat_id)
            return await CallbackQuery.message.reply_text("⏸ Duraklatıldı!")

        elif action == "stop":
            await CallbackQuery.answer()
            await ArchMusic.stop_stream(chat_id)
            return await CallbackQuery.message.reply_text("⏹ Müzik kapatıldı!")

        elif action == "mute":
            if await is_muted(chat_id):
                await CallbackQuery.answer()
                return await CallbackQuery.message.reply_text("🔇 Zaten sessizde!")
            await mute_on(chat_id)
            return await CallbackQuery.message.reply_text("🔇 Sessize alındı!")

        elif action == "unmute":
            if not await is_muted(chat_id):
                await CallbackQuery.answer()
                return await CallbackQuery.message.reply_text("🔊 Zaten açık!")
            await mute_off(chat_id)
            return await CallbackQuery.message.reply_text("🔊 Ses açıldı!")

        else:
            return await CallbackQuery.answer("⚠️ Geçersiz işlem!", show_alert=True)

    except Exception as e:
        return await CallbackQuery.message.reply_text(f"⚠️ Hata: {e}")

  # ===============================================================
# 🎛 BUTON MENÜLERİNİ GÜNCELLEME
# ===============================================================
@app.on_callback_query(filters.regex("panel"))
@languageCB
async def panel_callbacks(client, CallbackQuery: CallbackQuery, _):
    try:
        command = CallbackQuery.data.split("|")
        video = True if command[1] == "v" else False
        channel = True if command[2] == "c" else False
        fplay = True if command[3] == "f" else False

        if video:
            buttons = video_markup(_, CallbackQuery.message.chat.id)
            return await CallbackQuery.edit_message_reply_markup(
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        else:
            buttons = audio_markup(_, CallbackQuery.message.chat.id)
            return await CallbackQuery.edit_message_reply_markup(
                reply_markup=InlineKeyboardMarkup(buttons)
            )

    except Exception as e:
        return await CallbackQuery.message.reply_text(f"⚠️ Panel hatası: {e}")


print("[ParsMuzikBot] ✅ playcallback.py yüklendi - Buton sistemi aktif!")
