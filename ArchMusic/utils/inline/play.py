# -*- coding: utf-8 -*-
#
# Inline Keyboards for Play / Stream
# Uyumlu: play.py ve playcallback.py
# Not: strings çeviri sözlüğünden (_["..."]) gelen anahtarları kullanır.

from pyrogram.types import InlineKeyboardButton
from typing import List


# ---------------------------------------------------------
# Yardımcı: Tek satır buton dizisi oluşturucu
def _row(*buttons: InlineKeyboardButton) -> List[InlineKeyboardButton]:
    return [*buttons]


# =========================================================
# Arama sonucu: Tek parça için seçim (Ses / Video)
# play.py -> track_markup(...)
# =========================================================
def track_markup(_, videoid: str, user_id: int, channel: str, fplay: str):
    # channel: "g" (group) / "c" (channel)
    # fplay: "d" (queue sonu) / "f" (forceplay)
    return [
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


# =========================================================
# Playlist için seçim (YouTube / Spotify / Apple)
# play.py -> playlist_markup(...)
# ptype: "yt" | "spplay" | "spalbum" | "spartist" | "apple"
# =========================================================
def playlist_markup(_, videoid: str, user_id: int, ptype: str, channel: str, fplay: str):
    return [
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


# =========================================================
# Canlı yayın (m3u8 / live) için
# play.py -> livestream_markup(...)
# mode: "a" (ses) | "v" (video)
# =========================================================
def livestream_markup(_, videoid: str, user_id: int, mode: str, channel: str, fplay: str):
    return [
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


# =========================================================
# Slider (sonraki/önceki arama sonucu)
# play.py -> slider_markup(...)
# query_type: 0 / 1 (iç mantıkta sayfa yönü)
# =========================================================
def slider_markup(_, videoid: str, user_id: int, query: str, query_type: int, channel: str, fplay: str):
    query = f"{query[:20]}" if query else ""
    return [
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


# =========================================================
# Akış sırasında kontrol paneli (genel)
# Bazı modüller stream_markup(...) kullanıyor
# =========================================================
def stream_markup(_, videoid: str, chat_id: int):
    return [
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
        _row(
            InlineKeyboardButton(text=_["CLOSEMENU_BUTTON"], callback_data="close"),
        ),
    ]


# =========================================================
# Ses odaklı kontrol paneli (playcallback.py import eder)
# =========================================================
def audio_markup(_, chat_id: int):
    return [
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
        _row(
            InlineKeyboardButton(text=_["CLOSEMENU_BUTTON"], callback_data="close"),
        ),
    ]


# =========================================================
# Video odaklı kontrol paneli (playcallback.py import eder)
# =========================================================
def video_markup(_, chat_id: int):
    return [
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
        _row(
            InlineKeyboardButton(text=_["CLOSEMENU_BUTTON"], callback_data="close"),
        ),
    ]
# =========================================================
# Telegram Ses/Video Basit Panel (Zorunlu FIX)
# ArchMusic/core/call.py tarafından import edilir
# =========================================================
def telegram_markup(_, chat_id: int):
    return [
        [
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
        [
            InlineKeyboardButton(text="🔁 Loop", callback_data=f"ADMIN Loop|{chat_id}"),
            InlineKeyboardButton(text="🔇 Mute", callback_data=f"ADMIN Mute|{chat_id}"),
            InlineKeyboardButton(text="🔊 Unmute", callback_data=f"ADMIN Unmute|{chat_id}"),
        ],
        [
            InlineKeyboardButton(text=_["CLOSEMENU_BUTTON"], callback_data="close"),
        ]
    ]
