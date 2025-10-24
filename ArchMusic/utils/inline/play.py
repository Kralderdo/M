# -*- coding: utf-8 -*-
#
# Inline Keyboards for Play / Stream
# Uyumlu: core/call.py, plugins/admins/callback.py, plugins/play/*
# Not: strings çeviri sözlüğünden (_["..."]) gelen anahtarları kullanır.

from typing import List, Optional
from pyrogram.types import InlineKeyboardButton

# ---------------------------------------------------------
# Ayar: marka satırı (kaldırmak istersen "" yap)
BRANDING_TEXT: Optional[str] = "⚙️ Powered by Pars Müzik"

# ---------------------------------------------------------
# Yardımcı: Tek satır buton dizisi
def _row(*buttons: InlineKeyboardButton) -> List[InlineKeyboardButton]:
    return [*buttons]

# Yardımcı: Marka satırı (isteğe bağlı)
def _brand_row() -> List[InlineKeyboardButton]:
    if not BRANDING_TEXT:
        return []
    return _row(InlineKeyboardButton(text=BRANDING_TEXT, callback_data="nonclickable"))

# =========================================================
# Arama sonucu: Tek parça seçim (Ses / Video)
# play.py -> track_markup(...)
# =========================================================
def track_markup(_, videoid: str, user_id: int, channel: str, fplay: str):
    # channel: "g" (group) / "c" (channel)
    # fplay: "d" (queue sonu) / "f" (forceplay)
    rows = [
        _row(
            InlineKeyboardButton(
                text=_["P_B_1"],  # ▶️ Müzik Oynat
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],  # 🎬 Video Oynat
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
            ),
        ),
        _row(
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
            )
        ),
    ]
    br = _brand_row()
    if br: rows.insert(0, br)
    return rows

# =========================================================
# Playlist için seçim (YouTube / Spotify / Apple)
# play.py -> playlist_markup(...)
# ptype: "yt" | "spplay" | "spalbum" | "spartist" | "apple"
# =========================================================
def playlist_markup(_, videoid: str, user_id: int, ptype: str, channel: str, fplay: str):
    rows = [
        _row(
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"YukkiPlaylists {videoid}|{user_id}|{ptype}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"YukkiPlaylists {videoid}|{user_id}|{ptype}|v|{channel}|{fplay}",
            ),
        ),
        _row(
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
            )
        ),
    ]
    br = _brand_row()
    if br: rows.insert(0, br)
    return rows

# =========================================================
# Canlı yayın (m3u8 / live)
# play.py -> livestream_markup(...)
# mode: "a" (ses) | "v" (video)
# =========================================================
def livestream_markup(_, videoid: str, user_id: int, mode: str, channel: str, fplay: str):
    rows = [
        _row(
            InlineKeyboardButton(
                text=_["P_B_3"],  # 🔴 Canlı Oynat
                callback_data=f"LiveStream {videoid}|{user_id}|{mode}|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["CLOSEMENU_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
            ),
        )
    ]
    br = _brand_row()
    if br: rows.insert(0, br)
    return rows

# =========================================================
# Slider (önceki/sonraki arama sonucu)
# play.py -> slider_markup(...)
# query_type: int (iç sayfalama bilgisi)
# =========================================================
def slider_markup(_, videoid: str, user_id: int, query: str, query_type: int, channel: str, fplay: str):
    query = f"{(query or '')[:20]}"
    rows = [
        _row(
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
            ),
        ),
        _row(
            InlineKeyboardButton(
                text="❮",
                callback_data=f"slider B|{query_type}|{query}|{user_id}|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {query}|{user_id}",
            ),
            InlineKeyboardButton(
                text="❯",
                callback_data=f"slider F|{query_type}|{query}|{user_id}|{channel}|{fplay}",
            ),
        ),
    ]
    br = _brand_row()
    if br: rows.insert(0, br)
    return rows

# =========================================================
# Genel akış kontrol paneli
# core/call.py ve bazı modüller stream_markup ister
# =========================================================
def stream_markup(_, videoid: str, chat_id: int):
    rows = [
        _row(
            InlineKeyboardButton(text="⏮ 10", callback_data=f"ADMIN 1|{chat_id}"),
            InlineKeyboardButton(text="⏭ 10", callback_data=f"ADMIN 2|{chat_id}"),
            InlineKeyboardButton(text="⏮ 30", callback_data=f"ADMIN 3|{chat_id}"),
            InlineKeyboardButton(text="⏭ 30", callback_data=f"ADMIN 4|{chat_id}"),
        ),
        _row(
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
        ),
        _row(InlineKeyboardButton(text=_["CLOSEMENU_BUTTON"], callback_data="close")),
    ]
    br = _brand_row()
    if br: rows.insert(0, br)
    return rows

# =========================================================
# Telegram odaklı minimal panel (bazı sürümler çağırıyor)
# core/call.py -> telegram_markup import eder
# =========================================================
def telegram_markup(_, chat_id: int):
    rows = [
        _row(
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
        ),
        _row(InlineKeyboardButton(text=_["CLOSEMENU_BUTTON"], callback_data="close")),
    ]
    br = _brand_row()
    if br: rows.insert(0, br)
    return rows

# =========================================================
# Ses odaklı kontrol paneli
# plugins/play/playcallback.py -> audio_markup import eder
# =========================================================
def audio_markup(_, chat_id: int):
    rows = [
        _row(
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
        ),
        _row(
            InlineKeyboardButton(text="🔇 Mute", callback_data=f"ADMIN Mute|{chat_id}"),
            InlineKeyboardButton(text="🔊 Unmute", callback_data=f"ADMIN Unmute|{chat_id}"),
            InlineKeyboardButton(text="🔁 Loop", callback_data=f"ADMIN Loop|{chat_id}"),
            InlineKeyboardButton(text="🔀 Shuffle", callback_data=f"ADMIN Shuffle|{chat_id}"),
        ),
        _row(InlineKeyboardButton(text=_["CLOSEMENU_BUTTON"], callback_data="close")),
    ]
    br = _brand_row()
    if br: rows.insert(0, br)
    return rows

# =========================================================
# Video odaklı kontrol paneli
# plugins/play/playcallback.py -> video_markup import eder
# =========================================================
def video_markup(_, chat_id: int):
    rows = [
        _row(
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
        ),
        _row(
            InlineKeyboardButton(text="⏮ 10", callback_data=f"ADMIN 1|{chat_id}"),
            InlineKeyboardButton(text="⏭ 10", callback_data=f"ADMIN 2|{chat_id}"),
            InlineKeyboardButton(text="⏮ 30", callback_data=f"ADMIN 3|{chat_id}"),
            InlineKeyboardButton(text="⏭ 30", callback_data=f"ADMIN 4|{chat_id}"),
        ),
        _row(InlineKeyboardButton(text=_["CLOSEMENU_BUTTON"], callback_data="close")),
    ]
    br = _brand_row()
    if br: rows.insert(0, br)
    return rows

# =========================================================
# Panel sayfalama (bazı sürümler import ediyor)
# plugins/admins/callback.py -> panel_markup_1/2/3 import eder
# =========================================================
def panel_markup_1(_, videoid: str, chat_id: int):
    rows = [
        _row(
            InlineKeyboardButton(text="⏸ Pause", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="▶️ Resume", callback_data=f"ADMIN Resume|{chat_id}"),
        ),
        _row(
            InlineKeyboardButton(text="⏯ Skip", callback_data=f"ADMIN Skip|{chat_id}"),
            InlineKeyboardButton(text="⏹ Stop", callback_data=f"ADMIN Stop|{chat_id}"),
        ),
        _row(InlineKeyboardButton(text="🔁 Replay", callback_data=f"ADMIN Replay|{chat_id}")),
    ]
    br = _brand_row()
    if br: rows.insert(0, br)
    return rows

def panel_markup_2(_, videoid: str, chat_id: int):
    rows = [
        _row(
            InlineKeyboardButton(text="🔇 Mute", callback_data=f"ADMIN Mute|{chat_id}"),
            InlineKeyboardButton(text="🔊 Unmute", callback_data=f"ADMIN Unmute|{chat_id}"),
        ),
        _row(
            InlineKeyboardButton(text="🔀 Shuffle", callback_data=f"ADMIN Shuffle|{chat_id}"),
            InlineKeyboardButton(text="🔁 Loop", callback_data=f"ADMIN Loop|{chat_id}"),
        ),
    ]
    br = _brand_row()
    if br: rows.insert(0, br)
    return rows

def panel_markup_3(_, videoid: str, chat_id: int):
    rows = [
        _row(
            InlineKeyboardButton(text="⏮ 10", callback_data=f"ADMIN 1|{chat_id}"),
            InlineKeyboardButton(text="⏭ 10", callback_data=f"ADMIN 2|{chat_id}"),
        ),
        _row(
            InlineKeyboardButton(text="⏮ 30", callback_data=f"ADMIN 3|{chat_id}"),
            InlineKeyboardButton(text="⏭ 30", callback_data=f"ADMIN 4|{chat_id}"),
        ),
    ]
    br = _brand_row()
    if br: rows.insert(0, br)
    return rows
