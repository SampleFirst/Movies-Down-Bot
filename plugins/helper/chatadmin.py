import asyncio
from pyrogram import Client, filters
from pyrogram.types import ChatMember
from info import *


# Define a command to list admins and owners
@Client.on_message(filters.command("admins") & filters.user(ADMINS))
async def list_admins(client, message):
    try:
        chat_id = message.chat.id
        chat = await client.get_chat(chat_id)  # Get the chat object
        async for member in chat.iter_chat_members():
            if member.status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
                admin_info = {
                    'User ID': member.user.id,
                    'Username': member.user.username,
                    'Status': member.status,
                    'Custom Title': member.custom_title,
                    'Can Be Edited': member.can_be_edited,
                    'Privileges': member.privileges,
                    'Permissions': member.permissions,
                }
                await message.reply(f"Admin/Owner Info:\n{admin_info}")

        await message.reply("End of Admins/Owners List")

    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}")
