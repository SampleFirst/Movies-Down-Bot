from pyrogram import Client, filters
from database.users_chats_db import db
from info import ADMINS 

# Define a function to handle the /showinvitelinks command
@Client.on_message(filters.command("showinvitelinks"))
async def show_invite_links_command(client, message):
    # Get the user who sent the command
    user = message.from_user
    user_id = user.id

    # Check if the user is authorized to use this command (you can implement your logic here)
    if user_id in ADMINS:
        # Retrieve and send the invite links for saved chats
        chat_ids = await db.get_all_saved_chats()  # Implement this function in your Database class
        if chat_ids:
            invite_links = []
            for chat_id in chat_ids:
                invite_link = await db.get_chat_invite_link(chat_id)
                if invite_link:
                    invite_links.append(f"Chat ID: {chat_id}, Invite Link: {invite_link}")

            if invite_links:
                response = "\n".join(invite_links)
                await message.reply(f"Here are the saved chat invite links:\n\n{response}")
            else:
                await message.reply("No saved chat invite links found.")
        else:
            await message.reply("No saved chats found.")
    else:
        await message.reply("You are not authorized to use this command.")
