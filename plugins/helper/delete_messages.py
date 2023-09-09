import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from info import ADMINS


@Client.on_message(filters.command("purge") & (filters.group | filters.supergroup | filters.channel))
async def purge(client, message):
    # Check if the chat type is a supergroup, group, or channel
    chat_type = ""
    if message.chat.type == 'group':
        chat_type = "group"
    elif message.chat.type == 'supergroup':
        chat_type = "supergroup"
    elif message.chat.type == 'channel':
        chat_type = "channel"
    
    # Check if the user sending the command is an admin
    is_admin = message.from_user.id in ADMINS
    if not is_admin:
        await message.reply_text("You are not authorized to use this command in this {}.".format(chat_type), quote=True)
        return

    # Send a status message to indicate the purge is in progress
    status_message = await message.reply_text("Purging in {}...".format(chat_type), quote=True)

    count_deleted_messages = 0  # Initialize count_deleted_messages
    message_ids = []

    if message.reply_to_message:
        # Collect message IDs for deletion within the defined range
        async for msg in client.iter_history(
            chat_id=message.chat.id,
            reverse=True,
            offset_id=message.reply_to_message.message_id,
        ):
            message_ids.append(msg.message_id)
            # Delete messages in batches of 100 to avoid rate limits
            if len(message_ids) == 100:
                await client.delete_messages(
                    chat_id=message.chat.id,
                    message_ids=message_ids
                )
                count_deleted_messages += len(message_ids)
                message_ids = []

        # Delete any remaining messages
        if len(message_ids) > 0:
            await client.delete_messages(
                chat_id=message.chat.id,
                message_ids=message_ids
            )
            count_deleted_messages += len(message_ids)

    # Edit the status message to show the number of deleted messages
    await status_message.edit_text(f"Deleted {count_deleted_messages} messages in {}.".format(count_deleted_messages, chat_type))

    # Wait for 5 seconds before deleting the status message
    await asyncio.sleep(5)
    await status_message.delete()
