import os
import re

from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import state
from clients import call_py
from core.api import fetch_youtube_link
from core.guards import check_abuse, is_admin
from core.playback import play_music_core


async def play_command(client, message):
    chat_id = message.chat.id

    if await check_abuse(message.from_user.id):
        return await message.reply_text("⏳ **Slow down.**")

    query = " ".join(message.command[1:])
    requester = message.from_user.mention

    if not query:
        return await message.reply_text("❌ **Usage:** `/play <song name or url>`")

    status_msg = await message.reply_text("🔎 **Searching...**")

    if "youtu.be" in query:
        m = re.search(r"youtu\.be/([^?&]+)", query)
        if m:
            query = f"https://www.youtube.com/watch?v={m.group(1)}"

    result = await fetch_youtube_link(query)
    if not result:
        return await status_msg.edit_text("❌ No results found.")

    song_info = {
        "title": result.get("title"),
        "url": result.get("link"),
        "duration": str(result.get("duration", "0")),
        "thumb": result.get("thumbnail"),
        "req": requester,
        "user_id": message.from_user.id,
        "file_path": None,
        "bot_id": client.me.id,
    }

    if chat_id not in state.chat_queues:
        state.chat_queues[chat_id] = []
    state.chat_queues[chat_id].append(song_info)

    if len(state.chat_queues[chat_id]) == 1:
        await play_music_core(client, chat_id, song_info, status_msg)
    else:
        queue_pos = len(state.chat_queues[chat_id]) - 1
        queue_text = (
            f"<b>✨ ᴀᴅᴅᴇᴅ ᴛᴏ ǫᴜᴇᴜᴇ:</b>\n\n"
            f"<b>❍ ᴛɪᴛʟᴇ:</b> {song_info['title']}\n"
            f"<b>❍ ᴘᴏsɪᴛɪᴏɴ:</b> {queue_pos}"
        )
        await status_msg.edit_text(
            queue_text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("⏭ Skip", callback_data="skip"),
                InlineKeyboardButton("🗑 Clear", callback_data="clear"),
            ]]),
        )


async def stop_command(client, message):
    chat_id = message.chat.id
    if not await is_admin(client, chat_id, message.from_user.id):
        return
    if chat_id in state.progress_tasks:
        state.progress_tasks[chat_id].cancel()
        del state.progress_tasks[chat_id]
    state.chat_queues.pop(chat_id, None)
    state.paused_chats.discard(chat_id)
    try:
        await call_py.leave_call(chat_id)
    except Exception:
        pass
    await message.reply_text("⏹ **Stopped playback.**")


async def skip_command(client, message):
    chat_id = message.chat.id
    if not await is_admin(client, chat_id, message.from_user.id):
        return
    if chat_id in state.progress_tasks:
        state.progress_tasks[chat_id].cancel()
        del state.progress_tasks[chat_id]
    state.paused_chats.discard(chat_id)

    if chat_id in state.chat_queues and state.chat_queues[chat_id]:
        done = state.chat_queues[chat_id].pop(0)
        fp = done.get("file_path")
        if fp and os.path.exists(fp):
            try:
                os.remove(fp)
            except Exception:
                pass
        if state.chat_queues[chat_id]:
            await message.reply_text("⏭ **Skipping...**")
            await play_music_core(client, chat_id, state.chat_queues[chat_id][0])
        else:
            try:
                await call_py.leave_call(chat_id)
            except Exception:
                pass
            await message.reply_text("✅ **Queue ended.**")
    else:
        await message.reply_text("❌ **Nothing to skip.**")


async def clear_command(client, message):
    chat_id = message.chat.id
    if not await is_admin(client, chat_id, message.from_user.id):
        return
    if chat_id in state.chat_queues and len(state.chat_queues[chat_id]) > 1:
        state.chat_queues[chat_id] = [state.chat_queues[chat_id][0]]
        await message.reply_text("🗑 **Queue cleared.**")
    else:
        await message.reply_text("❌ **Queue is already empty.**")


async def pause_command(client, message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return
    try:
        await call_py.pause(message.chat.id)
        state.paused_chats.add(message.chat.id)
        await message.reply_text("⏸ **Paused.**")
    except Exception:
        pass


async def resume_command(client, message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return
    try:
        await call_py.resume(message.chat.id)
        state.paused_chats.discard(message.chat.id)
        await message.reply_text("▶️ **Resumed.**")
    except Exception:
        pass
