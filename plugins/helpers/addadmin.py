from pyrogram import Client, filters
from pyrogram.errors import UserNotParticipant
from pyrogram.types import ChatPermissions
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

    try:
        chat_info = await client.get_chat(message.chat.id)
        is_supergroup = chat_info.is_verified

        if is_supergroup:
            privileges = ChatPermissions(
                can_change_info=True,
                can_delete_messages=True,
                can_manage_chat=True,
                can_restrict_members=True,
                can_invite_users=True,
                can_pin_messages=True,
                can_promote_members=True
            )
            await message.reply(f"User added as an admin in supergroup {message.chat.id} with specified privileges.")
        else:
            privileges = ChatPermissions(
                can_change_info=True,
                can_delete_messages=True,
                can_manage_chat=True,
                can_restrict_members=True,
                can_invite_users=True,
                can_pin_messages=True,
                can_promote_members=True
            )
            await message.reply(f"User added as an admin in group {message.chat.id} with specified privileges.")

        await client.promote_chat_member(message.chat.id, user_id, permissions=privileges)
    except UserNotParticipant:
        await message.reply(f"The user must be a member of the chat to use this command.")
    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}")
