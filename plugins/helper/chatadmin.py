from pyrogram import Client, filters
from pyrogram.types import ChatMember
from info import ADMINS

privilege_names = {
    "can_manage_chat": "Manage Chat",
    "can_delete_messages": "Delete Messages",
    "can_manage_video_chats": "Manage Video Chats",
    "can_restrict_members": "Restrict Members",
    "can_promote_members": "Promote Members",
    "can_change_info": "Change Info",
    "can_post_messages": "Post Messages",
    "can_edit_messages": "Edit Messages",
    "can_invite_users": "Invite Users",
    "can_pin_messages": "Pin Messages",
    "is_anonymous": "Anonymous"
}

permission_names = {
    "can_send_messages": "Send Messages",
    "can_send_media_messages": "Send Media Messages",
    "can_send_other_messages": "Send Other Messages",
    "can_send_polls": "Send Polls",
    "can_add_web_page_previews": "Add Web Page Previews",
    "can_change_info": "Change Info",
    "can_invite_users": "Invite Users",
    "can_pin_messages": "Pin Messages"
}


@Client.on_message(filters.command("admins") & filters.user(ADMINS))
async def list_admins(client, message):
    try:
        chat_id = int(message.command[1])  # Extract the chat_id from the command, e.g., "/admins 12345"
    except (IndexError, ValueError):
        await message.reply("Invalid chat ID. Please use '/admins CHAT_ID' to list admins.")
        return

    try:
        # Get all chat members (using .iter_chat_members to get an async generator)
        async for member in client.iter_chat_members(chat_id):
            if member.status == "administrator":
                admins.append(member)
    except Exception as e:
        await message.reply(f"Error getting chat members: {str(e)}")
        return

    if not admins:
        await message.reply("There are no administrators in this chat.")
        return

    admin_info_list = []
    for admin in admins:
        admin_info = f"{admin.user.mention} - {admin.user.first_name}\n"
        privileges = []
        permissions = []

        # Check if the chat is a channel, group, or supergroup
        chat = await client.get_chat(chat_id)
        if chat.type in ["channel", "supergroup"]:
            for privilege, privilege_name in privilege_names.items():
                if getattr(admin, privilege):
                    privileges.append(privilege_name)
        else:  # For groups
            for permission, permission_name in permission_names.items():
                if getattr(admin.permissions, permission):
                    permissions.append(permission_name)

        if privileges:
            admin_info += "Privileges: " + ", ".join(privileges)
        if permissions:
            admin_info += "Permissions: " + ", ".join(permissions)

        admin_info_list.append(admin_info)

    response_message = f"Admins in {chat.title}:\n\n" + "\n\n".join(admin_info_list)
    await message.reply(response_message)
    
