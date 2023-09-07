import asyncio
from pyrogram import Client, filters
from pyrogram.types import ChatMember
from info import ADMINS

# Define a command to list admins and owners
@Client.on_message(filters.command("admins") & filters.user(ADMINS))
async def list_admins(client, message):
    try:
        chat_id = message.chat.id
        # Use the client object to iterate over chat members
        async for member in client.iter_chat_members(chat_id):
            if member.status in ["administrator", "creator"]:
                admin_info = {
                    'User ID': member.user.id,
                    'Username': member.user.username,
                    'Status': member.status,
                    'Custom Title': member.custom_title if member.custom_title else "None",
                    'Can Be Edited': member.can_be_edited,
                    'Privileges': member.privileges,
                    'Permissions': member.permissions,
                }
                await message.reply(f"Admin/Owner Info:\n{admin_info}")

        await message.reply("End of Admins/Owners List")

    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}")
