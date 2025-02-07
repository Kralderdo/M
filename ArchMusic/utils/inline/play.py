import math

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from ArchMusic.utils.formatters import time_to_seconds

    def get_progress_bar(percentage):
    umm = math.floor(percentage)

    if 0 < umm <= 10:
        return "⚪─────────"
    elif 10 < umm <= 20:
        return "━⚪────────"
    elif 20 < umm <= 30:
        return "━━⚪───────"
    elif 30 < umm <= 40:
        return "━━━⚪──────"
    elif 40 < umm <= 50:
        return "━━━━⚪─────"
    elif 50 < umm <= 60:
        return "━━━━━⚪────"
    elif 60 < umm <= 70:
        return "━━━━━━⚪───"
    elif 70 < umm <= 80:
        return "━━━━━━━⚪──"
    elif 80 < umm <= 90:
        return "━━━━━━━━⚪─"
    elif 90 < umm <= 100:
        return "━━━━━━━━━⚪"
    else:
        return "───────────"

def get_progress_bare(percentage):
    umm = math.floor(percentage)

   
    if 0 < umm <= 10:
        return "♨ 𝐃ɳѕ 𝐌υ𝗌𝗂𝖼 𝐁𝖾𝗌𝗍 𝐅𝖾α𝗍υ𝗋𝖾𝗌 ♨"
    elif 5 <= umm < 20:
        return "♨ 𝐃ɳѕ 𝐌υ𝗌𝗂𝖼 𝐅α𝗏ⱺ𝗋𝗂𝗍𝖾 ρᥣα𝗒ᥣ𝗂𝗌𝗍 ♨"
    elif 10 <= umm < 30:
        return "♨ 𝐃ɳѕ 𝐌υ𝗌𝗂𝖼 𝐌𝗂ᥣᥣ𝗂ⱺ𐓣 𝐒ⱺ𐓣𝗀𝗌 ♨"
    elif 15 <= umm < 40:
        return "♨ 𝐃ɳѕ 𝐌υ𝗌𝗂𝖼 𝐄α𝗌𝗂ᥣ𝗒 𝐒𝗍𝗋𝖾αꭑ ♨"
    elif 20 <= umm < 50:
        return "♨ 𝐋ⱺω-𝐒ρ𝖾𝖾ᑯ 𝐒𝗍𝗋𝖾αꭑ𝗂𐓣𝗀 ♨"
    elif 25 <= umm < 60:
        return "♨ 𝐃ɳѕ 𝐌υ𝗌𝗂𝖼 𝐁𝗂𝗀 𝐃α𝗍αᑲα𝗌ɦ ♨"
    elif 30 <= umm < 70:
        return "♨ 𝐅𝗋𝖾𝖾 𝐃ⱺω𐓣ᥣⱺαᑯ 𝐌υ𝗌𝗂𝖼 ♨"
    elif 35 <= umm < 80:
        return "♨ 𝐃ɳѕ 𝐌υ𝗌𝗂𝖼 𝐅α𝗏ⱺ𝗋𝗂𝗍𝖾 ρᥣα𝗒ᥣ𝗂𝗌𝗍 ♨"
    elif 40 <= umm < 90:
        return "♨ 𝐋α𝗀 𝐅𝗋𝖾𝖾 𝐆ααɳα 𝐌υ𝗌𝗂𝖼 ♨"
    elif 45 <= umm < 100:
        return "♨ 𝐌υѕι𝚌 𝐒𝗍υᑯ𝗂ⱺ ♨"
    else:
        return "♨ 𝐓ɦ𝖾 𝐒ⱺ𐓣𝗀 𝚰𝗌 𝐎𝗏𝖾𝗋 ♨"

def get_progress_baree(percentage):
    umm = math.floor(percentage)
    
    if 0 < umm <= 100:
        return "᪥⋟ 𝐃ɳѕ 𝐌υ𝗌𝗂𝖼 ⋞᪥"
    elif 5 <= umm < 200:
        return "᪥⋟ 𝐃ɳѕ 𝐌υ𝗌𝗂𝖼 ⋞᪥"
    else:
        return "᪥⋟ 𝐃ɳѕ 𝐌υ𝗌𝗂𝖼 ⋞᪥"
        
        
        
def stream_markup_timer(_, videoid, chat_id, played, dur):
    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)
    percentage = (played_sec / duration_sec) * 100
    bar = get_progress_bar(percentage)
    bare = get_progress_bare(percentage)
    baree = get_progress_baree(percentage) # using for getting the bar
    buttons = [
        [
            InlineKeyboardButton(
                text=f"{baree}",
                callback_data="GetTimer",
            )
        ],
        [
            InlineKeyboardButton(
                text=f"{played} {bar} {dur}",
                callback_data="GetTimer",
            )
        ],
        [
            InlineKeyboardButton(
                text=f"{bare}",
                callback_data="GetTimer",
            )
        ],
          [
            InlineKeyboardButton(
                text="𝐔ρ𝖽αтєѕ", url=f"https://t.me/Dns_Official_Channel"
            ),
            InlineKeyboardButton(text=_["CLOSEMENU_BUTTON"], callback_data="𝖢𝗅𝗈𝗌𝖾"
          ),
         
        
            InlineKeyboardButton(
                text="𝐒υρρσɾƚ", url=f"https://t.me/DNS_NETWORK"),
        ],
    ]
    return buttons



def telegram_markup_timer(_, chat_id, played, dur):
    bar = random.choice(selections)
    buttons = [

        [
            
            InlineKeyboardButton(text="▷",callback_data=f"ADMIN Resume|{chat_id}",),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="‣‣", callback_data=f"ADMIN Skip|{chat_id}"),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
             
        ],
    ]
    return buttons

        

# Rest of the functions remain the same...



## Inline without Timer Bar


def stream_markup(_, videoid, chat_id):
    buttons = [
        [
             
        
        ],
        
    ]
    return buttons


def telegram_markup(_, chat_id):
    buttons = [
        [
            
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
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
            )
        ],
    ]
    return buttons


def playlist_markup(_, videoid, user_id, ptype, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"ArchMusicPlaylists {videoid}|{user_id}|{ptype}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"ArchMusicPlaylists {videoid}|{user_id}|{ptype}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
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


def slider_markup(
    _, videoid, user_id, query, query_type, channel, fplay
):
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
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {query}|{user_id}",
            ),
            InlineKeyboardButton(
                text="❯",
                callback_data=f"slider F|{query_type}|{query}|{user_id}|{channel}|{fplay}",
            ),
        ],
    ]
    return buttons


## Cpanel Markup


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
            InlineKeyboardButton(
                text="⏯ Skip", callback_data=f"ADMIN Skip|{chat_id}"
            ),
            InlineKeyboardButton(
                text="⏹ Stop", callback_data=f"ADMIN Stop|{chat_id}"
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
            InlineKeyboardButton(
                text="🔇 Mute", callback_data=f"ADMIN Mute|{chat_id}"
            ),
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
            InlineKeyboardButton(
                text="🔁 Loop", callback_data=f"ADMIN Loop|{chat_id}"
            ),
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
                text="⏮ 10 Seconds",
                callback_data=f"ADMIN 1|{chat_id}",
            ),
            InlineKeyboardButton(
                text="⏭ 10 Seconds",
                callback_data=f"ADMIN 2|{chat_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="⏮ 30 Seconds",
                callback_data=f"ADMIN 3|{chat_id}",
            ),
            InlineKeyboardButton(
                text="⏭ 30 Seconds",
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
