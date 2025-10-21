from typing import Dict, List, Union, Optional

from ArchMusic.core.mongo import mongodb

# Collections
queriesdb = mongodb.queries
userdb = mongodb.userstats
chattopdb = mongodb.chatstats
authuserdb = mongodb.authuser
gbansdb = mongodb.gban
sudoersdb = mongodb.sudoers
chatsdb = mongodb.chats
blacklist_chatdb = mongodb.blacklistChat
usersdb = mongodb.tgusersdb
playlistdb = mongodb.playlist
blockeddb = mongodb.blockedusers
privatedb = mongodb.privatechats
restart_db = mongodb.autorestart
settings_collection = mongodb.settings


# -------------------- Auto-Restart Settings --------------------

async def get_restart_settings() -> Dict[str, Union[bool, int]]:
    settings = await restart_db.find_one({"_id": "restart_config"})
    if not settings:
        settings = {"_id": "restart_config", "enabled": True, "interval": 360}
        await restart_db.insert_one(settings)
    return settings


async def update_restart_settings(enabled: Optional[bool] = None, interval: Optional[int] = None) -> Dict[str, Union[bool, int]]:
    settings = await get_restart_settings()
    update_data: Dict[str, Union[bool, int]] = {}

    if enabled is not None:
        update_data["enabled"] = enabled
    if interval is not None:
        update_data["interval"] = interval

    if update_data:
        await restart_db.update_one({"_id": "restart_config"}, {"$set": update_data})
        settings.update(update_data)

    return settings


# -------------------- Playlists --------------------

async def _get_playlists(chat_id: int) -> Dict[str, int]:
    _notes = await playlistdb.find_one({"chat_id": chat_id})
    if not _notes:
        return {}
    return _notes.get("notes", {})


async def get_playlist_names(chat_id: int) -> List[str]:
    return list((await _get_playlists(chat_id)).keys())


async def get_playlist(chat_id: int, name: str) -> Union[bool, dict]:
    _notes = await _get_playlists(chat_id)
    return _notes.get(name, False)


async def save_playlist(chat_id: int, name: str, note: dict):
    _notes = await _get_playlists(chat_id)
    _notes[name] = note
    await playlistdb.update_one({"chat_id": chat_id}, {"$set": {"notes": _notes}}, upsert=True)


async def delete_playlist(chat_id: int, name: str) -> bool:
    notesd = await _get_playlists(chat_id)
    if name in notesd:
        del notesd[name]
        await playlistdb.update_one({"chat_id": chat_id}, {"$set": {"notes": notesd}}, upsert=True)
        return True
    return False


# -------------------- Users (served) --------------------

async def is_served_user(user_id: int) -> bool:
    return bool(await usersdb.find_one({"user_id": user_id}))


async def get_served_users() -> list:
    users_list = []
    async for user in usersdb.find({"user_id": {"$gt": 0}}):
        users_list.append(user)
    return users_list


async def add_served_user(user_id: int):
    if await is_served_user(user_id):
        return
    return await usersdb.insert_one({"user_id": user_id})


# -------------------- Chats (served) --------------------

async def get_served_chats() -> list:
    chats_list = []
    async for chat in chatsdb.find({"chat_id": {"$lt": 0}}):
        chats_list.append(chat)
    return chats_list


async def is_served_chat(chat_id: int) -> bool:
    return bool(await chatsdb.find_one({"chat_id": chat_id}))


async def add_served_chat(chat_id: int):
    if await is_served_chat(chat_id):
        return
    return await chatsdb.insert_one({"chat_id": chat_id})


# -------------------- Blacklisted Chats --------------------

async def blacklisted_chats() -> list:
    chats_list = []
    async for chat in blacklist_chatdb.find({"chat_id": {"$lt": 0}}):
        chats_list.append(chat.get("chat_id"))
    return chats_list


async def blacklist_chat(chat_id: int) -> bool:
    if not await blacklist_chatdb.find_one({"chat_id": chat_id}):
        await blacklist_chatdb.insert_one({"chat_id": chat_id})
        return True
    return False


async def whitelist_chat(chat_id: int) -> bool:
    if await blacklist_chatdb.find_one({"chat_id": chat_id}):
        await blacklist_chatdb.delete_one({"chat_id": chat_id})
        return True
    return False


# -------------------- Private Served Chats --------------------

async def get_private_served_chats() -> list:
    chats_list = []
    async for chat in privatedb.find({"chat_id": {"$lt": 0}}):
        chats_list.append(chat)
    return chats_list


async def is_served_private_chat(chat_id: int) -> bool:
    return bool(await privatedb.find_one({"chat_id": chat_id}))


async def add_private_chat(chat_id: int):
    if await is_served_private_chat(chat_id):
        return
    return await privatedb.insert_one({"chat_id": chat_id})


async def remove_private_chat(chat_id: int):
    if not await is_served_private_chat(chat_id):
        return
    return await privatedb.delete_one({"chat_id": chat_id})


# -------------------- Auth Users --------------------

async def _get_authusers(chat_id: int) -> Dict[str, int]:
    _notes = await authuserdb.find_one({"chat_id": chat_id})
    if not _notes:
        return {}
    return _notes.get("notes", {})


async def get_authuser_names(chat_id: int) -> List[str]:
    return list((await _get_authusers(chat_id)).keys())


async def get_authuser(chat_id: int, name: str) -> Union[bool, dict]:
    _notes = await _get_authusers(chat_id)
    return _notes.get(name, False)


async def save_authuser(chat_id: int, name: str, note: dict):
    _notes = await _get_authusers(chat_id)
    _notes[name] = note
    await authuserdb.update_one({"chat_id": chat_id}, {"$set": {"notes": _notes}}, upsert=True)


async def delete_authuser(chat_id: int, name: str) -> bool:
    notesd = await _get_authusers(chat_id)
    if name in notesd:
        del notesd[name]
        await authuserdb.update_one({"chat_id": chat_id}, {"$set": {"notes": notesd}}, upsert=True)
        return True
    return False


# -------------------- GBan --------------------

async def get_gbanned() -> list:
    results = []
    async for user in gbansdb.find({"user_id": {"$gt": 0}}):
        results.append(user.get("user_id"))
    return results


async def is_gbanned_user(user_id: int) -> bool:
    return bool(await gbansdb.find_one({"user_id": user_id}))


async def add_gban_user(user_id: int):
    if await is_gbanned_user(user_id):
        return
    return await gbansdb.insert_one({"user_id": user_id})


async def remove_gban_user(user_id: int):
    if not await is_gbanned_user(user_id):
        return
    return await gbansdb.delete_one({"user_id": user_id})


# -------------------- Sudoers (FIXED) --------------------

async def _ensure_sudo_doc() -> Dict[str, Union[str, list]]:
    """
    sudoers dokümanı yoksa oluşturur ve döndürür.
    """
    doc = await sudoersdb.find_one({"sudo": "sudo"})
    if not doc:
        doc = {"sudo": "sudo", "sudoers": []}
        await sudoersdb.insert_one(doc)
    if "sudoers" not in doc or not isinstance(doc["sudoers"], list):
        doc["sudoers"] = []
        await sudoersdb.update_one({"sudo": "sudo"}, {"$set": {"sudoers": []}}, upsert=True)
    return doc


async def get_sudoers() -> list:
    doc = await _ensure_sudo_doc()
    return doc.get("sudoers", [])


async def add_sudo(user_id: int) -> bool:
    doc = await _ensure_sudo_doc()
    sudoers = doc.get("sudoers", [])

    # Zaten ekliyse tekrar ekleme
    if user_id in sudoers:
        return True

    sudoers.append(user_id)
    await sudoersdb.update_one({"sudo": "sudo"}, {"$set": {"sudoers": sudoers}}, upsert=True)
    return True


async def remove_sudo(user_id: int) -> bool:
    """
    Güvenli sudo silme:
    - Listede yoksa False döner
    - OWNER_ID asla silinmez
    - MongoDB'yi güvenli günceller
    """
    doc = await _ensure_sudo_doc()
    sudoers = doc.get("sudoers", [])

    # Kullanıcı listede değilse
    if user_id not in sudoers:
        return False

    # OWNER_ID koruması
    try:
        from config.config import OWNER_ID as OWNER_IDS  # type: ignore
    except Exception:
        OWNER_IDS = []
    try:
        if isinstance(OWNER_IDS, (list, tuple)) and user_id in OWNER_IDS:
            return False
    except Exception:
        pass

    # Filtreleyerek kaldır
    sudoers = [x for x in sudoers if x != user_id]
    await sudoersdb.update_one({"sudo": "sudo"}, {"$set": {"sudoers": sudoers}}, upsert=True)
    return True


# -------------------- Queries --------------------

async def get_queries() -> int:
    chat_id = 98324
    mode = await queriesdb.find_one({"chat_id": chat_id})
    if not mode:
        return 0
    return int(mode.get("mode", 0))


async def set_queries(mode: int):
    chat_id = 98324
    queries = await queriesdb.find_one({"chat_id": chat_id})
    if queries:
        mode = int(queries.get("mode", 0)) + mode
    return await queriesdb.update_one({"chat_id": chat_id}, {"$set": {"mode": mode}}, upsert=True)


# -------------------- Top Chats --------------------

async def get_top_chats() -> dict:
    results: Dict[int, int] = {}
    async for chat in chattopdb.find({"chat_id": {"$lt": 0}}):
        chat_id = chat.get("chat_id")
        total = 0
        for i in chat.get("vidid", {}):
            counts_ = chat["vidid"][i].get("spot", 0)
            if counts_ > 0:
                total += counts_
        if chat_id is not None:
            results[chat_id] = total
    return results


async def get_global_tops() -> dict:
    results: Dict[str, dict] = {}
    async for chat in chattopdb.find({"chat_id": {"$lt": 0}}):
        for i in chat.get("vidid", {}):
            counts_ = chat["vidid"][i].get("spot", 0)
            title_ = chat["vidid"][i].get("title", "")
            if counts_ > 0:
                if i not in results:
                    results[i] = {"spot": counts_, "title": title_}
                else:
                    results[i]["spot"] = results[i]["spot"] + counts_
    return results


async def get_particulars(chat_id: int) -> Dict[str, int]:
    ids = await chattopdb.find_one({"chat_id": chat_id})
    if not ids:
        return {}
    return ids.get("vidid", {})


async def get_particular_top(chat_id: int, name: str) -> Union[bool, dict]:
    ids = await get_particulars(chat_id)
    if name in ids:
        return ids[name]


async def update_particular_top(chat_id: int, name: str, vidid: dict):
    ids = await get_particulars(chat_id)
    ids[name] = vidid
    await chattopdb.update_one({"chat_id": chat_id}, {"$set": {"vidid": ids}}, upsert=True)


# -------------------- Top Users --------------------

async def get_userss(chat_id: int) -> Dict[str, int]:
    ids = await userdb.find_one({"chat_id": chat_id})
    if not ids:
        return {}
    return ids.get("vidid", {})


async def get_user_top(chat_id: int, name: str) -> Union[bool, dict]:
    ids = await get_userss(chat_id)
    if name in ids:
        return ids[name]


async def update_user_top(chat_id: int, name: str, vidid: dict):
    ids = await get_userss(chat_id)
    ids[name] = vidid
    await userdb.update_one({"chat_id": chat_id}, {"$set": {"vidid": ids}}, upsert=True)


async def get_topp_users() -> dict:
    results: Dict[int, int] = {}
    async for chat in userdb.find({"chat_id": {"$gt": 0}}):
        user_id = chat.get("chat_id")
        total = 0
        for i in chat.get("vidid", {}):
            counts_ = chat["vidid"][i].get("spot", 0)
            if counts_ > 0:
                total += counts_
        if user_id is not None:
            results[user_id] = total
    return results


# -------------------- Blocked Users --------------------

async def get_banned_users() -> list:
    results = []
    async for user in blockeddb.find({"user_id": {"$gt": 0}}):
        results.append(user.get("user_id"))
    return results


async def get_banned_count() -> int:
    users = blockeddb.find({"user_id": {"$gt": 0}})
    users = await users.to_list(length=100000)
    return len(users)


async def is_banned_user(user_id: int) -> bool:
    return bool(await blockeddb.find_one({"user_id": user_id}))


async def add_banned_user(user_id: int):
    if await is_banned_user(user_id):
        return
    return await blockeddb.insert_one({"user_id": user_id})


async def remove_banned_user(user_id: int):
    if not await is_banned_user(user_id):
        return
    return await blockeddb.delete_one({"user_id": user_id})
