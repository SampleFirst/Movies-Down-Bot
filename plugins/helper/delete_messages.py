import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from info import ADMINS

@Client.on_message(filters.command("purge") & (filters.group | filters.channel))                   
async def purge(client, message):
    chat_type = message.chat.type  # Get the chat type

    if chat_type not in (enums.ChatType.SUPERGROUP, enums.ChatType.CHANNEL):
        await message.reply_text("This command can only be used in supergroups or channels.", quote=True)
        return

    # Check if the user sending the command is an admin
    if not message.from_user or message.from_user.id not in ADMINS:
        await message.reply_text("You are not authorized to use this command in this {}.".format(chat_type), quote=True)
        return

    # Send a status message to indicate the purge is in progress
    status_message = await message.reply_text("Purging in {}...".format(chat_type), quote=True)

    count_deleted_messages = 0  # Initialize count_deleted_messages

    if message.reply_to_message:
        try:
            async for msg in client.get_history(
                chat_id=message.chat.id,
                offset_id=message.reply_to_message.message_id + 1,  # Add 1 to start after the replied message
            ):
                await client.delete_messages(
                    chat_id=message.chat.id,
                    message_ids=msg.message_id
                )
                count_deleted_messages += 1
        except Exception as e:
            await status_message.edit_text("An error occurred while purging messages: {}".format(str(e)))
            return

    # Edit the status message to show the number of deleted messages
    await status_message.edit_text("Deleted {} messages in {}.".format(count_deleted_messages, chat_type))
    
    # Wait for 5 seconds before deleting the status message
    await asyncio.sleep(5)
    await status_message.delete()
