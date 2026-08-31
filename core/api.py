import asyncio
import logging
import os
import time
import urllib.parse

import aiohttp
import yt_dlp

from config import COOKIES_FILE, DOWNLOAD_API_BASE, SEARCH_API_URL

logger = logging.getLogger(__name__)


async def fetch_youtube_link(query):
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{SEARCH_API_URL}/search?q={urllib.parse.quote(query)}"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, dict):
                        return data
                    if isinstance(data, list) and data:
                        return data[0]
        return None
    except Exception:
        return None


async def _download_via_api(youtube_url):
    try:
        unique = str(time.time())
        final_path = f"downloads/{unique}.mp3"
        endpoint = f"{DOWNLOAD_API_BASE}/download?url={urllib.parse.quote(youtube_url)}"
        async with aiohttp.ClientSession() as session:
            async with session.get(endpoint, timeout=aiohttp.ClientTimeout(total=60)) as resp:
                if resp.status != 200:
                    return None
                content_type = resp.headers.get("Content-Type", "")
                if "application/json" in content_type:
                    data = await resp.json()
                    direct_url = data.get("url") or data.get("link") or data.get("download_url")
                    if not direct_url:
                        return None
                    async with session.get(direct_url, timeout=aiohttp.ClientTimeout(total=120)) as audio_resp:
                        if audio_resp.status != 200:
                            return None
                        with open(final_path, "wb") as f:
                            async for chunk in audio_resp.content.iter_chunked(65536):
                                f.write(chunk)
                else:
                    with open(final_path, "wb") as f:
                        async for chunk in resp.content.iter_chunked(65536):
                            f.write(chunk)
        if os.path.exists(final_path) and os.path.getsize(final_path) > 0:
            return final_path
        return None
    except Exception as e:
        logger.warning(f"Download API failed: {e}")
        return None


def _yt_download(youtube_url, output_template):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "extractor_args": {
            "youtube": {
                "player_client": ["web", "mweb", "android"],
            }
        },
    }
    if COOKIES_FILE and os.path.exists(COOKIES_FILE):
        ydl_opts["cookiefile"] = COOKIES_FILE
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])


async def _download_via_ytdlp(youtube_url):
    try:
        unique = str(time.time())
        output_template = f"downloads/{unique}.%(ext)s"
        final_path = f"downloads/{unique}.mp3"
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _yt_download, youtube_url, output_template)
        if os.path.exists(final_path):
            return final_path
        for ext in ["m4a", "webm", "opus", "ogg"]:
            alt = f"downloads/{unique}.{ext}"
            if os.path.exists(alt):
                return alt
        return None
    except Exception as e:
        logger.warning(f"yt-dlp failed: {e}")
        return None


async def download_song(youtube_url):
    if DOWNLOAD_API_BASE:
        result = await _download_via_api(youtube_url)
        if result:
            return result
        logger.info("Download API failed, falling back to yt-dlp")
    return await _download_via_ytdlp(youtube_url)
