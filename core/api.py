import asyncio
import logging
import os
import time
import urllib.parse

import aiohttp
import yt_dlp

from config import COOKIES_FILE, SEARCH_API_URL

logger = logging.getLogger(__name__)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


async def fetch_youtube_link(query):
    """Search YouTube using the configured search API."""
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{SEARCH_API_URL}/search?q={urllib.parse.quote(query)}"

            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=15)
            ) as response:

                if response.status != 200:
                    logger.warning(
                        f"Search API returned HTTP {response.status}"
                    )
                    return None

                data = await response.json()

                if isinstance(data, dict):
                    return data

                if isinstance(data, list) and data:
                    return data[0]

        return None

    except Exception as e:
        logger.warning(f"YouTube search failed: {e}")
        return None


def _yt_download(youtube_url, output_template):
    """
    Download audio only with yt-dlp.
    No video format is downloaded.
    """

    ydl_opts = {
        # Audio only
        "format": "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio",

        "outtmpl": output_template,

        # Keep original audio instead of downloading a video
        "noplaylist": True,

        # Faster / cleaner output
        "quiet": True,
        "no_warnings": False,

        # Don't hang forever
        "socket_timeout": 30,
        "retries": 3,
        "fragment_retries": 3,

        # Avoid unnecessary playlist processing
        "extract_flat": False,

        # Extractor clients
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web", "mweb"],
            }
        },
    }

    # Use cookies only when the configured file actually exists.
    if COOKIES_FILE and os.path.isfile(COOKIES_FILE):
        ydl_opts["cookiefile"] = COOKIES_FILE

    logger.info(f"Starting yt-dlp audio download: {youtube_url}")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])


async def _download_via_ytdlp(youtube_url):
    """Run yt-dlp outside the asyncio event loop."""

    unique = str(int(time.time() * 1000))
    output_template = os.path.join(
        DOWNLOAD_DIR,
        f"{unique}.%(ext)s"
    )

    try:
        loop = asyncio.get_running_loop()

        await loop.run_in_executor(
            None,
            _yt_download,
            youtube_url,
            output_template
        )

        # Find the file produced by yt-dlp.
        base = os.path.join(DOWNLOAD_DIR, unique)

        for ext in ("m4a", "webm", "opus", "ogg", "mp3"):
            path = f"{base}.{ext}"

            if os.path.isfile(path) and os.path.getsize(path) > 0:
                logger.info(
                    f"Audio downloaded successfully: {path}"
                )
                return path

        logger.warning("yt-dlp finished but no audio file was found.")
        return None

    except Exception as e:
        logger.warning(f"yt-dlp failed: {e}")
        return None


async def download_song(youtube_url):
    """
    Main downloader used by playback.py.

    Returns:
        Local audio file path, or None on failure.
    """

    if not youtube_url:
        logger.warning("No YouTube URL supplied.")
        return None

    return await _download_via_ytdlp(youtube_url)
