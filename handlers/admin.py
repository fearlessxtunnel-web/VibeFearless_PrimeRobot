from pyrogram.types import ChatPermissions

from core.guards import is_admin


async def kick_user(client, m):
    if not await is_admin(client, m.chat.id, m.from_user.id):
        return
    if m.reply_to_message:
        await m.chat.ban_member(m.reply_to_message.from_user.id)
        await m.chat.unban_member(m.reply_to_message.from_user.id)
        await m.reply_text("👞 Kicked.")


async def ban_user(client, m):
    if not await is_admin(client, m.chat.id, m.from_user.id):
        return
    if m.reply_to_message:
        await m.chat.ban_member(m.reply_to_message.from_user.id)
        await m.reply_text("⛔ Banned.")


async def unban_user(client, m):
    if not await is_admin(client, m.chat.id, m.from_user.id):
        return
    if m.reply_to_message:
        await m.chat.unban_member(m.reply_to_message.from_user.id)
        await m.reply_text("✅ Unbanned.")


async def mute_user(client, m):
    if not await is_admin(client, m.chat.id, m.from_user.id):
        return
    if m.reply_to_message:
        await m.chat.restrict_member(
            m.reply_to_message.from_user.id,
            ChatPermissions(can_send_messages=False),
        )
        await m.reply_text("🔇 Muted.")


async def unmute_user(client, m):
    if not await is_admin(client, m.chat.id, m.from_user.id):
        return
    if m.reply_to_message:
        await m.chat.restrict_member(
            m.reply_to_message.from_user.id,
            ChatPermissions(can_send_messages=True),
        )
        await m.reply_text("🔊 Unmuted.")
