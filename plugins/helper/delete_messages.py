from pyrogram import Client, filters
from pyrogram.types import Message


# Define the command handler
@Client.on_message(filters.command("delete_messages") & filters.private)
async def delete_all_messages(client, message: Message):
    try:
        # Get the chat ID from the command arguments
        chat_id = message.command[1]

        # Check if the chat_id is valid (you might want to add more validation)
        if chat_id.isdigit():
            chat_id = int(chat_id)

            # Get all messages in the chat
            messages = await client.get_history(chat_id)

            # Delete each message in the chat
            for msg in messages:
                await client.delete_messages(chat_id, msg.message_id)

            # Notify the user that messages have been deleted
            await message.reply_text(f"All messages in chat {chat_id} have been deleted.")
        else:
            await message.reply_text("Invalid chat ID provided.")

    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")
