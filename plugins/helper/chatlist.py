from pyrogram import Client, filters
from pyrogram.types import Message
from info import ADMINS


# Define the command handler function
@Client.on_message(filters.command('list_chats') & filters.user(ADMINS))
def list_admin_chats(_, message: Message):
    try:
        # Check if the sender is the bot's admin
        if message.from_user.id in ADMINS:
            # Get a list of all chats where the bot is an admin
            chat_list = client.get_chat_members(message.chat.id)
            
            # Extract chat names and IDs
            chats_info = []
            for member in chat_list:
                if member.status == "administrator":
                    chat_info = f"Chat Name: {member.chat.title}, Chat ID: {member.chat.id}"
                    chats_info.append(chat_info)
            
            # Send the list of admin chats as a reply
            if chats_info:
                reply_text = "\n".join(chats_info)
                message.reply_text(f"List of admin chats:\n{reply_text}")
            else:
                message.reply_text("The bot is not an admin in any chat.")
        else:
            message.reply_text("You are not authorized to use this command.")
    except Exception as e:
        message.reply_text(f"An error occurred: {str(e)}")
