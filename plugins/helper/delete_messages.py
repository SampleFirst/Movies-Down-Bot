import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from info import ADMINS


@Client.on_message(filters.command("purge") & (filters.group | filters.channel))
async def purge(client, message):
    # Check if the chat type is a supergroup or channel
    if message.chat.type not in (enums.ChatType.SUPERGROUP, enums.ChatType.CHANNEL):
        return

    # Check if the user sending the command is an admin
    is_admin = message.from_user.id in ADMINS
    if not is_admin:
        await message.reply_text("You are not authorized to use this command.", quote=True)
        return

    # Send a status message to indicate the purge is in progress
    status_message = await message.reply_text("Purging...", quote=True)

    # Delete the original command message
    await message.delete()

    message_ids = []
    message = msg
    count_deleted_messages = 0

    if message.reply_to_message:
        # Collect message IDs for deletion
        for msg_id in range(message.reply_to_message.message_id, message.message_id):
            message_ids.append(msg_id)
            # Delete messages in batches of 100 to avoid rate limits
            if len(message_ids) == 100:
                await client.delete_messages(
                    chat_id=message.chat.id,
                    message_ids=message_ids,
                    revoke=True
                )
                count_deleted_messages += len(message_ids)
                message_ids = []

        # Delete any remaining messages
        if len(message_ids) > 0:
            await client.delete_messages(
                chat_id=message.chat.id,
                message_ids=message_ids,
                revoke=True
            )
            count_deleted_messages += len(message_ids)

    # Edit the status message to show the number of deleted messages
    await status_message.edit_text(f"Deleted {count_deleted_messages} messages")

    # Wait for 5 seconds before deleting the status message
    await asyncio.sleep(5)
    await status_message.delete()
