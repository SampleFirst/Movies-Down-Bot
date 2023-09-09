import asyncio
from pyrogram import Client, filters
from info import ADMINS
from database.users_chats_db import db

# Define a command to list admins and owners
@Client.on_message(filters.command("admins") & filters.user(ADMINS))
async def list_admins(client, message):
    try:
        chat_id = message.chat.id
        await message.reply("Fetching information about chat admins and owners...")

        # Use the db module to fetch chat admins and owners
        admins_owners = await db.get_chat_admins_owners(chat_id)
        
        if admins_owners:
            response_message = "Admins/Owners in this chat:\n\n"
            for admin_info in admins_owners:
                response_message += f"{admin_info}\n"
            
            # Send the response message with a split limit to avoid exceeding message length limits
            await message.reply_text(response_message, parse_mode="Markdown", quote=True)
        else:
            await message.reply("No Admins/Owners found in this chat.")

        await message.reply("End of Admins/Owners List")

    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}")


@Client.on_message(filters.command("adminslist") & filters.private)
async def extract_admins(client, message):
    if len(message.command) != 2:
        return await message.reply("Please provide a valid group chat ID.")
    
    chat_id = message.command[1]
    try:
        chat = await client.get_chat(int(chat_id))
        title = chat.title
    except:
        return await message.reply("Invalid chat ID or I'm not in the group.")

    admins = []

    async for admin in client.iter_chat_members(int(chat_id), filter='administrators'):
        admins.append(admin.user.username)

    await message.reply(f"Admins, Administrators, and Owners in {title}:\n\n{', '.join(admins)}")
    
