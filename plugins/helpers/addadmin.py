from pyrogram import Client, filters
from pyrogram.errors import UserNotParticipant
from pyrogram.types import ChatPrivileges
from info import ADMINS



# Define your command handler for adding admin in a group
@Client.on_message(filters.command("addgroupadmin") & filters.group)
async def add_group_admin(client, message):
    if message.from_user.id not in ADMINS:
        await message.reply("You must be an admin to use this command.")
        return

    if len(message.command) != 2:
        await message.reply("Usage: /addgroupadmin user_id")
        return

    user_id = int(message.command[1])

    for chat_id in chat_group_ids:
        try:
            chat_info = await client.get_chat(chat_id)
            is_supergroup = chat_info.is_verified  # Await the get_chat method and access 'is_verified'

            if is_supergroup:
                privileges = ChatPrivileges(
                    can_change_info=True,
                    can_delete_messages=True,
                    can_manage_video_chats=True,
                    can_restrict_members=True,
                    can_promote_members=True,
                    can_invite_users=True,
                    can_pin_messages=True,
                    is_anonymous=True,
                    can_manage_chat=True
                )
                await message.reply(f"User added as an admin in supergroup {chat_id} with specified privileges.")
            else:
                privileges = ChatPrivileges(
                    can_change_info=True,
                    can_delete_messages=True,
                    can_manage_video_chats=True,
                    can_restrict_members=True,
                    can_promote_members=True,
                    can_invite_users=True,
                    can_pin_messages=True
                )
                await message.reply(f"User added as an admin in group {chat_id} with specified privileges.")

            await client.promote_chat_member(chat_id, user_id, privileges=privileges)
        except UserNotParticipant:
            await message.reply(f"The user must be a member of the chat {chat_id} to use this command.")
        except Exception as e:
            await message.reply(f"An error occurred: {str(e)}")
            
