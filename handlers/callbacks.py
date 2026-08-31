import asyncio

from pyrogram.enums import ParseMode
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

import state
from core.guards import is_admin
from core.playback import play_music_core
from handlers.music import clear_command, pause_command, resume_command, skip_command, stop_command
from handlers.system import start_handler


async def callback_handler(client, query: CallbackQuery):
    data = query.data
    chat_id = query.message.chat.id
    user_id = query.from_user.id

    if data == "progress":
        return await query.answer("🎵 Live Playback")

    if data == "verify_assistant":
        if not await is_admin(client, chat_id, user_id):
            return await query.answer("❌ Admin only!", show_alert=True)
        if chat_id in state.chat_queues and state.chat_queues[chat_id]:
            await query.message.edit_text("🔄 <b>Continuing playback...</b>", parse_mode=ParseMode.HTML)
            asyncio.create_task(play_music_core(client, chat_id, state.chat_queues[chat_id][0], query.message))
        else:
            await query.message.edit_text("❌ <b>Queue is empty.</b>", parse_mode=ParseMode.HTML)
        return

    if data == "show_help":
        buttons = [
            [
                InlineKeyboardButton("🎵 Music", callback_data="help_music"),
                InlineKeyboardButton("🛡️ Admin", callback_data="help_admin"),
            ],
            [InlineKeyboardButton("🏠 Back", callback_data="go_back")],
        ]
        return await query.message.edit_text(
            "📜 <b>Commands</b>\n\nChoose a category:",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(buttons),
        )

    if data == "go_back":
        return await start_handler(client, query.message)

    if data == "help_music":
        return await query.message.edit_text(
            "<blockquote>🎵 <b>Music Commands</b></blockquote>\n\n"
            "<code>/play</code> — Play a song or URL\n"
            "<code>/skip</code> — Skip current song\n"
            "<code>/stop</code> — Stop playback\n"
            "<code>/pause</code> — Pause playback\n"
            "<code>/resume</code> — Resume playback\n"
            "<code>/clear</code> — Clear the queue",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="show_help")]]),
        )

    if data == "help_admin":
        return await query.message.edit_text(
            "<blockquote>🛡️ <b>Admin Commands</b></blockquote>\n\n"
            "<code>/kick</code> — Kick a user (reply)\n"
            "<code>/ban</code> — Ban a user (reply)\n"
            "<code>/unban</code> — Unban a user (reply)\n"
            "<code>/mute</code> — Mute a user (reply)\n"
            "<code>/unmute</code> — Unmute a user (reply)",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="show_help")]]),
        )

    if data in ["stop", "skip", "pause", "resume", "clear"]:
        if not await is_admin(client, chat_id, user_id):
            return await query.answer("❌ Admin only!", show_alert=True)
        if data == "stop":
            await stop_command(client, query.message)
        elif data == "skip":
            await skip_command(client, query.message)
        elif data == "pause":
            await pause_command(client, query.message)
        elif data == "resume":
            await resume_command(client, query.message)
        elif data == "clear":
            if chat_id in state.chat_queues and len(state.chat_queues[chat_id]) > 1:
                state.chat_queues[chat_id] = [state.chat_queues[chat_id][0]]
                await query.answer("🗑 Queue cleared.")
                await query.message.edit_text("🗑 <b>Queue cleared.</b>", parse_mode=ParseMode.HTML)
            else:
                await query.answer("❌ Queue is already empty.")
        try:
            await query.answer()
        except Exception:
            pass
