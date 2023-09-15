import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from info import SUPPORT_CHAT, LOG_CHANNEL, ADMINS
from database.users_chats_db import db
from utils import temp

# A dictionary to keep track of users and their warning counts
user_warning_counts = {}


@Client.on_message(filters.text & filters.group)
async def handle_text_message(client, message: Message):
    user_id = message.from_user.id
    is_admin = user_id in ADMINS

    if not is_admin:
        # Check for violations
        violations = []

        if "http://" in message.text or "https://" in message.text:
            violations.append("link")

        if (
            f"@{message.from_user.username}" in message.text
            and "@admin" not in message.text
            and "@request" not in message.text
        ):
            violations.append("username")

        keywords = ["join", "bio"]
        for keyword in keywords:
            if keyword in message.text.lower():
                violations.append("keyword_" + keyword)

        # Initialize warning_msg with an empty string
        warning_msg = ""

        # Handle violations
        for violation in violations:
            user_warning_counts.setdefault(user_id, {"link_count": 0, "username_count": 0, "ban_word_count": 0})
            user_warning_counts[user_id][violation + "_count"] += 1

            count = user_warning_counts[user_id][violation + "_count"]

            if count == 1:
                warning_msg = f"You've violated the group rules by sending a {violation}, {message.from_user.first_name}. This is your first warning."
            elif count == 2:
                warning_msg = f"You've violated the group rules by sending a {violation}, {message.from_user.first_name}. This is your final warning. One more {violation} and you will be banned."
            else:
                try:
                    await message.chat.ban_member(user_id=user_id)
                except Exception as error:
                    await client.send_message(LOG_CHANNEL, f"Error banning user {user_id}: {str(error)}")
                else:
                    warning_msg = f"You have been banned for repeatedly violating the group rules by sending a {violation}, {message.from_user.first_name}."

            if count >= 3:
                # Send the reason for the warning to the LOG_CHANNEL
                await client.send_message(LOG_CHANNEL, f"User {user_id} received a warning for a {violation}. Reason: {violation.capitalize()} detected - {message.text}")

        if warning_msg:
            # Only send a warning message if warning_msg is not empty
            warning = await message.reply_text(warning_msg)
            await asyncio.sleep(120)
            await warning.delete()
            await message.delete()

        # Reset violation counts after a while (e.g., a day)
        await asyncio.sleep(24 * 60 * 60)  # Sleep for a day
        if user_id in user_warning_counts:
            for violation in violations:
                user_warning_counts[user_id][violation + "_count"] = 0
