import time

from pyrogram.enums import ChatMemberStatus

import state
from config import MAIN_OWNER, RATE_LIMIT_COUNT, RATE_LIMIT_WINDOW


async def is_admin(client, chat_id, user_id):
    if user_id == MAIN_OWNER:
        return True
    if user_id == getattr(client, "clone_owner", MAIN_OWNER):
        return True
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception:
        return False


async def check_abuse(user_id):
    now = time.time()
    if user_id not in state.user_command_history:
        state.user_command_history[user_id] = []
    history = [t for t in state.user_command_history[user_id] if now - t < RATE_LIMIT_WINDOW]
    if len(history) >= RATE_LIMIT_COUNT:
        return True
    history.append(now)
    state.user_command_history[user_id] = history
    return False
