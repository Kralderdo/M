import random

from pyrogram.types import InlineKeyboardButton

selection = [
    "▁▄▂▇▄▅▄▅▃",
    "▁▃▇▂▅▇▄▅▃",
    "▃▁▇▂▅▃▄▃▅",
    "▃▄▂▄▇▅▃▅▁",
    "▁▃▄▂▇▃▄▅▃",
    "▃▁▄▂▅▃▇▃▅",
    "▁▇▄▂▅▄▅▃▄",
    "▁▃▅▇▂▅▄▃▇",
    "▃▅▂▅▇▁▄▃▁",
    "▇▅▂▅▃▄▃▁▃",
    "▃▇▂▅▁▅▄▃▁",
    "▅▄▇▂▅▂▄▇▁",
    "▃▅▂▅▃▇▄▅▃",
]


def stream_markup_timer(_, videoid, chat_id, played, dur):
    played_sec = time_to_sec(played)
    total_sec = time_to_sec(dur)
    if total_sec == 0:
        total_sec = 1
    ratio = played_sec / total_sec
    pos = int(ratio * 8)

    # İlerleme çubuğu (tam görseldeki gibi)
    bar_symbols = ["➖"] * 8
    if pos >= len(bar_symbols):
        pos = len(bar_symbols) - 1
    bar_symbols[pos] = "🔘"
    bar = "".join(bar_symbols)

    # Butonlar
    buttons = [
        [
            InlineKeyboardButton("🚀 prenses Bots 🚀", url="https://t.me/sesizlikkkDusmanimizzzz")
        ],
        [
            InlineKeyboardButton(f"{played}  ⟪ {bar} ⟫  {dur}", callback_data="nonclickable")
        ],
        [
            InlineKeyboardButton("⏮", callback_data=f"ADMIN 1|{chat_id}"),
            InlineKeyboardButton("⏸", callback_data=f"pausevc {chat_id}"),
            InlineKeyboardButton("⏭", callback_data=f"ADMIN 2|{chat_id}"),
            InlineKeyboardButton("⏹", callback_data=f"stopvc {chat_id}"),
        ],
        [
            InlineKeyboardButton("✅ Listeye Ekle", callback_data=f"add_playlist {videoid}"),
            InlineKeyboardButton("🔮 Kontrol Paneli", callback_data=f"PanelMarkup None|{chat_id}"),
        ],
    ]
    return buttons

    total_sec = time_to_sec(dur)
    if total_sec == 0:
        total_sec = 1

    x, y = str(round(played_sec / total_sec, 1)).split(".")
    pos = int(y)

    line = "─"
    circle = "●"

    bar = line * (pos - 1)
    bar += circle
    bar += line * (10 - len(bar))

    buttons = [
        [
            InlineKeyboardButton("▶️", callback_data=f"resumevc {chat_id}"),
            InlineKeyboardButton("⏸️", callback_data=f"pausevc {chat_id}"),
            InlineKeyboardButton("⏭️", callback_data=f"skipvc {chat_id}"),
            InlineKeyboardButton("⏹️", callback_data=f"stopvc {chat_id}"),
        ],
        [
            InlineKeyboardButton(
                text="🔮 PRENSES 𝘽𝙊𝙏𝙎 🔮",
                url="https://t.me/sesizlikkkDusmanimizzzz"
            )
        ],
        [
            InlineKeyboardButton(
                text=_["PL_B_2"],
                callback_data=f"add_playlist {videoid}",
            ),
            InlineKeyboardButton(
                text=_["PL_B_3"],
                callback_data=f"PanelMarkup None|{chat_id}",
            ),
        ],
    ]
    return buttons


def time_to_sec(time_str):
    parts = list(map(int, time_str.split(":")))
    return parts[0] * 60 + parts[1] if len(parts) == 2 else 0

def telegram_markup_timer(_, chat_id, played, dur, videoid):
    played_sec = time_to_sec(played)
    total_sec = time_to_sec(dur)
    if total_sec == 0:
        total_sec = 1
    ratio = played_sec / total_sec
    pos = int(ratio * 8)

    bar_symbols = ["➖"] * 8
    if pos >= len(bar_symbols):
        pos = len(bar_symbols) - 1
    bar_symbols[pos] = "🔘"
    bar = "".join(bar_symbols)

    buttons = [
        [
            InlineKeyboardButton("🚀 Prenses Bots 🚀", url="https://t.me/sesizlikkkDusmanimizzzz")
        ],
        [
            InlineKeyboardButton(f"{played} ⟪ {bar} ⟫ {dur}", callback_data="nonclickable")
        ],
        [
            InlineKeyboardButton("[⏮]", callback_data=f"ADMIN 1|{chat_id}"),
            InlineKeyboardButton("[⏸]", callback_data=f"pausevc {chat_id}"),
            InlineKeyboardButton("[▶️]", callback_data=f"resumevc {chat_id}"),
            InlineKeyboardButton("[⏭]", callback_data=f"ADMIN 2|{chat_id}"),
            InlineKeyboardButton("[⏹]", callback_data=f"stopvc {chat_id}"),
        ],
        [
            InlineKeyboardButton("✅ Listeye Ekle", callback_data=f"add_playlist {videoid}"),
            InlineKeyboardButton("🔮 Kontrol Paneli", callback_data=f"PanelMarkup None|{chat_id}"),
        ],
    ]
    return buttons


def stream_markup(_, videoid, chat_id):
    buttons = [
        [
            InlineKeyboardButton(text="🔁 TEKRARLA", callback_data=f"ADMIN Loop|{chat_id}"),
                
        ],
            [
            InlineKeyboardButton(text="⏮ 10",callback_data=f"ADMIN 1|{chat_id}",),
            InlineKeyboardButton(text="⏭ 10 ",callback_data=f"ADMIN 2|{chat_id}",),
             InlineKeyboardButton(text="⏮ 30 ",callback_data=f"ADMIN 3|{chat_id}",),
            InlineKeyboardButton(text="⏭ 30 ",callback_data=f"ADMIN 4|{chat_id}",),
        ],
        [
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
        [InlineKeyboardButton(text=_["CLOSEMENU_BUTTON"], callback_data="close")],
    ]
    return buttons


def telegram_markup_timer(_, chat_id, played, dur):
    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)
    percentage = (played_sec / duration_sec) * 100

    bar = get_progress_bar(percentage)  # using for getting the bar

    buttons = [
        [
            InlineKeyboardButton(
                text=f"{played} {bar} {dur}",
                callback_data="GetTimer",
            )
        ],
        [
            InlineKeyboardButton(
                text=_["PL_B_3"],
                callback_data=f"PanelMarkup None|{chat_id}",
            ),
        ],
        [
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
        [
            InlineKeyboardButton(text=_["CLOSEMENU_BUTTON"], callback_data="close"),
        ],
    ]
    return buttons


def telegram_markup(_, chat_id):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["PL_B_3"],
                callback_data=f"PanelMarkup None|{chat_id}",
            ),
        ],
        [
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
        [
            InlineKeyboardButton(text=_["CLOSEMENU_BUTTON"], callback_data="close"),
        ],
    ]
    return buttons


## Search Query Inline


def track_markup(_, videoid, user_id, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"], callback_data=f"forceclose {videoid}|{user_id}"
            )
        ],
    ]
    return buttons


def playlist_markup(_, videoid, user_id, ptype, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"YukkiPlaylists {videoid}|{user_id}|{ptype}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"YukkiPlaylists {videoid}|{user_id}|{ptype}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"], callback_data=f"forceclose {videoid}|{user_id}"
            ),
        ],
    ]
    return buttons


## Live Stream Markup


def livestream_markup(_, videoid, user_id, mode, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_3"],
                callback_data=f"LiveStream {videoid}|{user_id}|{mode}|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["CLOSEMENU_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
            ),
        ],
    ]
    return buttons


## Slider Query Markup


def slider_markup(_, videoid, user_id, query, query_type, channel, fplay):
    query = f"{query[:20]}"
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="❮",
                callback_data=f"slider B|{query_type}|{query}|{user_id}|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"], callback_data=f"forceclose {query}|{user_id}"
            ),
            InlineKeyboardButton(
                text="❯",
                callback_data=f"slider F|{query_type}|{query}|{user_id}|{channel}|{fplay}",
            ),
        ],
    ]
    return buttons


def panel_markup_1(_, videoid, chat_id):
    buttons = [
        [
            InlineKeyboardButton(
                text="⏸ Pause", callback_data=f"ADMIN Pause|{chat_id}"
            ),
            InlineKeyboardButton(
                text="▶️ Resume",
                callback_data=f"ADMIN Resume|{chat_id}",
            ),
        ],
        [
            InlineKeyboardButton(text="⏯ Skip", callback_data=f"ADMIN Skip|{chat_id}"),
            InlineKeyboardButton(text="⏹ Stop", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
        [
            InlineKeyboardButton(
                text="🔁 Replay ", callback_data=f"ADMIN Replay|{chat_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                text="◀️",
                callback_data=f"Pages Back|0|{videoid}|{chat_id}",
            ),
            InlineKeyboardButton(
                text="🔙 Back",
                callback_data=f"MainMarkup {videoid}|{chat_id}",
            ),
            InlineKeyboardButton(
                text="▶️",
                callback_data=f"Pages Forw|0|{videoid}|{chat_id}",
            ),
        ],
    ]
    return buttons


def panel_markup_2(_, videoid, chat_id):
    buttons = [
        [
            InlineKeyboardButton(text="🔇 Mute", callback_data=f"ADMIN Mute|{chat_id}"),
            InlineKeyboardButton(
                text="🔊 Unmute",
                callback_data=f"ADMIN Unmute|{chat_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="🔀 Shuffle",
                callback_data=f"ADMIN Shuffle|{chat_id}",
            ),
            InlineKeyboardButton(text="🔁 Loop", callback_data=f"ADMIN Loop|{chat_id}"),
        ],
        [
            InlineKeyboardButton(
                text="◀️",
                callback_data=f"Pages Back|1|{videoid}|{chat_id}",
            ),
            InlineKeyboardButton(
                text="🔙 Back",
                callback_data=f"MainMarkup {videoid}|{chat_id}",
            ),
            InlineKeyboardButton(
                text="▶️",
                callback_data=f"Pages Forw|1|{videoid}|{chat_id}",
            ),
        ],
    ]
    return buttons


def panel_markup_3(_, videoid, chat_id):
    buttons = [
        [
            InlineKeyboardButton(
                text="⏮ 10 seconds",
                callback_data=f"ADMIN 1|{chat_id}",
            ),
            InlineKeyboardButton(
                text="⏭ 10 seconds",
                callback_data=f"ADMIN 2|{chat_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="⏮ 30 seconds",
                callback_data=f"ADMIN 3|{chat_id}",
            ),
            InlineKeyboardButton(
                text="⏭ 30 seconds",
                callback_data=f"ADMIN 4|{chat_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="◀️",
                callback_data=f"Pages Back|2|{videoid}|{chat_id}",
            ),
            InlineKeyboardButton(
                text="🔙 Back",
                callback_data=f"MainMarkup {videoid}|{chat_id}",
            ),
            InlineKeyboardButton(
                text="▶️",
                callback_data=f"Pages Forw|2|{videoid}|{chat_id}",
            ),
        ],
    ]
    return buttons
