from pyrogram import Client, filters
from pyrogram.types import ChatMember
from info import *


@Client.on_message(filters.command("admins") & filters.user(ADMINS))
async def list_admins(client, message):
    try:
        chat_id = message.chat.id
        members = await client.get_chat_members(chat_id)

        admin_list = []

        for member in members:
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
                admin_list.append(admin_info)

        if admin_list:
            admin_list_text = '\n'.join([f"{key}: {value}" for admin_info in admin_list for key, value in admin_info.items()])
            await message.reply(f"Admins and Owners in this chat:\n{admin_list_text}")
        else:
            await message.reply("There are no Admins or Owners in this chat.")

    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}")

