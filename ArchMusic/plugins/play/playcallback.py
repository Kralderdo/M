# -*- coding: utf-8 -*-
#
# ParsMuzikBot - Play Callback Controller (FULL)
# Telegram Blue • TR UI • OWNER/SUDO güvenlik
# by @Kralderdo

from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup
from config import BANNED_USERS, OWNER_ID
from ArchMusic import app, YouTube
from ArchMusic.core.call import ArchMusic
from ArchMusic.utils.decorators.language import languageCB
from ArchMusic.utils.inline.play import (
    stream_markup,
    track_markup,
    slider_markup,          # slider kullanmıyoruz ama import kalabilir
    playlist_markup,
    livestream_markup,
)
from ArchMusic.utils.stream.stream import stream
from ArchMusic.utils import time_to_seconds
import config


# ──────────────────────────────────────────────────────────
# Güvenlik – sadece OWNER/SUDO kullansın
def authorized(user_id: int) -> bool:
    try:
        return int(user_id) in OWNER_ID
    except Exception:
        return False

# Premium imza
BRAND_SIGNATURE = (
    "🎧 PARS MUSIC SYSTEM\n"
    "🔥 Telegram'ın En Hızlı Müzik Botu\n"
    "📢 @Pars_Sohbet_TR"
)


# ──────────────────────────────────────────────────────────
# ▶️ MusicStream (Müzik/Video Başlatma)
# callback_data: "MusicStream {videoid}|{user_id}|a|c|d"
#                                 0          1       2 3 4
#   mode: a=audio v=video
#   channel: c/g
#   fplay: f/d
# ──────────────────────────────────────────────────────────
@app.on_callback_query(filters.regex(r"^MusicStream ") & ~BANNED_USERS)
@languageCB
async def music_stream_cb(client, cq: CallbackQuery, _):
    try:
        data = cq.data.strip().split("|")
        videoid = data[0].replace("MusicStream ", "").strip()
        req_user = int(data[1]) if len(data) > 1 and data[1].isdigit() else None
        mode = data[2] if len(data) > 2 else "a"      # a / v
        channel = True if len(data) > 3 and data[3] == "c" else False
        fplay = True if len(data) > 4 and data[4] == "f" else False

        chat_id = cq.message.chat.id
        caller_id = cq.from_user.id

        # Yetki
        if not authorized(caller_id):
            return await cq.answer("⛔ Bu butonu kullanma yetkin yok!", show_alert=True)

        await cq.answer("⏳ İşleniyor...")

        # YouTube ayrıntıları
        url = f"https://www.youtube.com/watch?v={videoid}"
        try:
            details, _track_id = await YouTube.track(url)
        except Exception as e:
            return await cq.message.reply_text(f"❌ YouTube verisi alınamadı: `{e}`")

        # Süre limiti
        if details.get("duration_min"):
            dur_sec = time_to_seconds(details["duration_min"])
            if dur_sec and dur_sec > config.DURATION_LIMIT:
                lim = config.DURATION_LIMIT_MIN
                return await cq.message.reply_text(f"⛔ En fazla {lim} dk uzunluğunda çalabilirim.")

        # Çalma
        try:
            await stream(
                _,
                cq.message,
                caller_id,
                details,
                chat_id,
                cq.from_user.first_name,
                chat_id,
                video=True if mode == "v" else False,
                streamtype="youtube",
                forceplay=fplay,
            )
        except Exception as e:
            return await cq.message.reply_text(f"⚠️ Akış hatası: `{type(e).__name__}`")

        # Başarı mesajı + kontrol butonları
        modetxt = "🎬 Video" if mode == "v" else "🎧 Ses"
        caption = (
            f"✅ **Çalma Başladı**\n"
            f"• **Mod:** {modetxt}\n"
            f"• **Parça:** {details.get('title','Bilinmiyor')}\n"
            f"{BRAND_SIGNATURE}"
        )
        try:
            btn = InlineKeyboardMarkup(stream_markup(_, videoid, chat_id))
            # Foto/Caption varsa
            await cq.message.edit_caption(caption, reply_markup=btn)
        except Exception:
            # Yoksa yeni mesaj
            await cq.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(stream_markup(_, videoid, chat_id)))

    except Exception as e:
        return await cq.message.reply_text(f"⚠️ MusicStream Hatası: `{e}`")


# ──────────────────────────────────────────────────────────
# 🔴 LiveStream (YouTube canlı)
# callback_data: "LiveStream {videoid}|{user_id}|a/v|c/g|f/d"
# ──────────────────────────────────────────────────────────
@app.on_callback_query(filters.regex(r"^LiveStream ") & ~BANNED_USERS)
@languageCB
async def live_stream_cb(client, cq: CallbackQuery, _):
    try:
        data = cq.data.strip().split("|")
        videoid = data[0].replace("LiveStream ", "").strip()
        mode = data[2] if len(data) > 2 else "a"
        chat_id = cq.message.chat.id

        if not authorized(cq.from_user.id):
            return await cq.answer("⛔ Yetkin yok!", show_alert=True)

        await cq.answer("📡 Canlı başlatılıyor...")

        url = f"https://www.youtube.com/watch?v={videoid}"
        # Bazı repolarda stream_call canlı için yeterli olur
        try:
            await ArchMusic.stream_call(url)
        except Exception:
            # Fallback: normal stream()
            try:
                details, _ = await YouTube.track(url)
                await stream(_, cq.message, cq.from_user.id, details, chat_id, cq.from_user.first_name, chat_id,
                             video=True if mode == "v" else False, streamtype="youtube", forceplay=True)
            except Exception as e:
                return await cq.message.reply_text(f"⚠️ Canlı yayın hatası: `{e}`")

        cap = f"🔴 **Canlı Yayın Başlatıldı** — {'🎬 Video' if mode=='v' else '🎧 Ses'}\n{BRAND_SIGNATURE}"
        try:
            await cq.message.edit_caption(cap, reply_markup=InlineKeyboardMarkup(stream_markup(_, videoid, chat_id)))
        except Exception:
            await cq.message.reply_text(cap, reply_markup=InlineKeyboardMarkup(stream_markup(_, videoid, chat_id)))

    except Exception as e:
        return await cq.message.reply_text(f"⚠️ LiveStream Hatası: `{e}`")


# ──────────────────────────────────────────────────────────
# 🎛 Yönetim – Pause / Resume / Stop / Skip / Loop / Seek
# callback_data: "ADMIN <Action>|<chat_id>"
#   Action: Pause, Resume, Stop, Skip, Loop, 1,2,3,4 (geri/ileri 10/30sn)
# ──────────────────────────────────────────────────────────
@app.on_callback_query(filters.regex(r"^ADMIN ") & ~BANNED_USERS)
@languageCB
async def admin_callbacks(client, cq: CallbackQuery, _):
    try:
        if not authorized(cq.from_user.id):
            return await cq.answer("⛔ Bu paneli kullanamazsın!", show_alert=True)

        parts = cq.data.split("|")
        action = parts[0].replace("ADMIN ", "").strip()
        chat_id = int(parts[1]) if len(parts) > 1 else cq.message.chat.id

        await cq.answer()

        if action == "Pause":
            await ArchMusic.pause_stream(chat_id)
            return await cq.message.reply_text("⏸ **Duraklatıldı**")

        elif action == "Resume":
            await ArchMusic.resume_stream(chat_id)
            return await cq.message.reply_text("▶️ **Devam ediyor**")

        elif action == "Stop":
            await ArchMusic.stop_stream(chat_id)
            return await cq.message.reply_text("⏹ **Durduruldu**")

        elif action == "Skip":
            try:
                await ArchMusic.skip_stream(chat_id)
                return await cq.message.reply_text("⏭ **Sonrakine geçildi**")
            except Exception:
                await ArchMusic.stop_stream(chat_id)
                return await cq.message.reply_text("⏭ **Atlandı (stop)**")

        elif action == "Loop":
            try:
                await ArchMusic.loop_stream(chat_id)
                return await cq.message.reply_text("🔁 **Tekrar modu aktif**")
            except Exception:
                return await cq.message.reply_text("ℹ️ **Tekrar modu bu sürümde desteklenmiyor**")

        elif action in {"1", "2", "3", "4"}:
            delta = {"1": -10, "2": 10, "3": -30, "4": 30}[action]
            try:
                await ArchMusic.seek_stream(chat_id, delta)
                sign = "⏮" if delta < 0 else "⏭"
                return await cq.message.reply_text(f"{sign} **{abs(delta)} saniye**")
            except Exception:
                return await cq.message.reply_text("ℹ️ **İleri/Geri sarma bu sürümde desteklenmiyor**")

        else:
            return await cq.answer("❗ Bilinmeyen işlem", show_alert=True)

    except Exception as e:
        return await cq.message.reply_text(f"⚠️ Panel Hatası: `{e}`")


# ──────────────────────────────────────────────────────────
# 🔊 Ses Kontrol – VOLUME|up|chat / VOLUME|down|chat
# ──────────────────────────────────────────────────────────
@app.on_callback_query(filters.regex(r"^VOLUME\|") & ~BANNED_USERS)
async def volume_control(client, cq: CallbackQuery):
    try:
        if not authorized(cq.from_user.id):
            return await cq.answer("⛔ Yetkin yok!", show_alert=True)

        parts = cq.data.split("|")
        action = parts[1]
        chat_id = int(parts[2]) if len(parts) > 2 else cq.message.chat.id

        await cq.answer()

        if action == "up":
            try:
                await ArchMusic.change_volume(chat_id, 10)
                return await cq.message.reply_text("🔊 Ses artırıldı **(+10)**")
            except Exception:
                return await cq.message.reply_text("ℹ️ Bu sürüm ses değiştirmeyi desteklemiyor.")

        elif action == "down":
            try:
                await ArchMusic.change_volume(chat_id, -10)
                return await cq.message.reply_text("🔉 Ses azaltıldı **(-10)**")
            except Exception:
                return await cq.message.reply_text("ℹ️ Bu sürüm ses değiştirmeyi desteklemiyor.")

    except Exception as e:
        return await cq.message.reply_text(f"⚠️ Ses kontrol hatası: `{e}`")


# ──────────────────────────────────────────────────────────
# 🧭 Diğer tıklamalar (Panel/Pages/GetTimer/close vb.) – Hata engelle
# ──────────────────────────────────────────────────────────
@app.on_callback_query(filters.regex(r"^(PanelMarkup|MainMarkup|Pages|GetTimer|close|forceclose|nonclickable)"))
async def misc_callbacks(client, cq: CallbackQuery):
    try:
        if cq.data.startswith("close") or cq.data.startswith("forceclose"):
            try:
                await cq.message.delete()
            except Exception:
                pass
            return await cq.answer()
        # Bilgi amaçlı sessiz onay
        return await cq.answer("🛠", show_alert=False)
    except Exception:
        pass


print("[ParsMuzikBot] ✅ playcallback.py yüklendi – FULL kontrol paneli aktif")
