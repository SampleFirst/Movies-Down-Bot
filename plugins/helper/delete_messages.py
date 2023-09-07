from pyrogram import Client, filters
from pyrogram.types import Message

# Define a command handler
@Client.on_message(filters.command("delete_msg"))
async def delete_all_messages(client, message: Message):
    # Check if the user is an administrator (or the bot itself) in the chat
    chat_id = message.command[1] if len(message.command) > 1 else None
    if chat_id:
        try:
            chat_id = int(chat_id)
        except ValueError:
            await message.reply("Invalid chat ID. Please provide a valid numeric chat ID.")
            return

        chat = await client.get_chat(chat_id)
        if not chat:
            await message.reply("Chat not found. Please provide a valid chat ID.")
            return

        # Check if the user has the necessary permissions to delete messages
        if chat.type in ["private", "group", "supergroup"]:
            # Delete all messages in the specified chat
            await message.delete(revoke=True)
            await message.reply(f"All messages in chat {chat.title} have been deleted.")
        else:
            await message.reply("This command can only be used in private chats, groups, or supergroups.")
    else:
        await message.reply("Please provide a valid chat ID with the command, like this: /delete_all <chat_id>")
