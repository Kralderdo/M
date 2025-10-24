# -*- coding: utf-8 -*-
# YouTube "Video unavailable" durumunda otomatik alternatif bulucu.
# Önce verilen videoid'i dener; olmazsa aynı sorguda oynatılabilir başka sonuç arar.
# Son çare SoundCloud araması dener (varsa).

from typing import Optional, Tuple

from ArchMusic import YouTube
try:
    # Soundcloud entegrasyonu varsa kullanırız; yoksa problemsiz geçer
    from ArchMusic import SoundCloud
    HAS_SC = True
except Exception:
    HAS_SC = False


async def get_playable_youtube(videoid: str, query: Optional[str] = None, live: bool = False
) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    """
    Dönüş: (source, new_videoid, stream_link, title)
      source: "youtube" | "soundcloud" | None
    """
    # 1) Verilen videoid’i doğrudan dene
    try:
        n, link, meta = await YouTube.video(videoid, live)  # meta: {"title":..., "duration":...} destekliyse
        if n != 0 and link:
            title = (meta.get("title") if isinstance(meta, dict) else None) or query or videoid
            return "youtube", videoid, link, title
    except Exception:
        pass

    # 2) Aynı sorgudan başka YouTube sonuçları dene
    q = (query or videoid or "").strip()
    if q:
        try:
            results = await YouTube.search(q, limit=8)  # beklenen: liste dict/obj
            for r in results or []:
                vid = (
                    getattr(r, "id", None)
                    or getattr(r, "videoid", None)
                    or getattr(r, "videoId", None)
                    or (isinstance(r, dict) and (r.get("id") or r.get("videoid") or r.get("videoId")))
                )
                title = (
                    getattr(r, "title", None)
                    or (isinstance(r, dict) and r.get("title"))
                    or q
                )
                if not vid or vid == videoid:
                    continue
                try:
                    n, link, meta = await YouTube.video(vid, live)
                    if n != 0 and link:
                        if isinstance(meta, dict) and meta.get("title"):
                            title = meta["title"]
                        return "youtube", vid, link, title
                except Exception:
                    continue
        except Exception:
            pass

    # 3) (Opsiyonel) SoundCloud fallback
    if HAS_SC and q:
        try:
            sc_results = await SoundCloud.search(q, limit=6)
            for tr in sc_results or []:
                # beklenen alan isimlerini esnek kontrol edelim
                stream = (
                    getattr(tr, "stream_url", None)
                    or (isinstance(tr, dict) and tr.get("stream_url"))
                )
                title = (
                    getattr(tr, "title", None)
                    or (isinstance(tr, dict) and tr.get("title"))
                    or q
                )
                if stream:
                    return "soundcloud", None, stream, title
        except Exception:
            pass

    # Hiçbiri oynatılabilir değilse
    return None, None, None, None
