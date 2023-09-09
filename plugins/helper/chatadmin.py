import asyncio
from pyrogram import Client, filters
from info import ADMINS
from database.users_chats_db import db
from pyrogram.types import ChatMember

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
    
@Client.on_message(filters.command("get_admins") & filters.private)
async def get_admins_list(client, message):
    chat_id = message.chat.id
    
    # Check if the user who sent the command is an admin or the owner
    user_info = await client.get_chat_member(chat_id, message.from_user.id)
    
    if user_info.status in ["administrator", "creator"]:
        # Get a list of all admins and the owner of the chat
        chat_members = await client.get_chat_members(chat_id)
        admin_list = []

        for member in chat_members:
            if member.status in ["administrator", "creator"]:
                admin_list.append(f"{member.user.first_name} ({member.user.id})")
        
        admins_text = "\n".join(admin_list)

        await message.reply(f"List of Admins and Owner:\n{admins_text}")
    else:
        await message.reply("You must be an admin or the owner to use this command.")


@Client.on_message(filters.command('show_admins') & filters.user(ADMINS))
def show_admins(client, message):
    chat_id = message.chat.id

    # Get the list of chat members
    chat_members = client.get_chat_members(chat_id)

    admins = []

    # Loop through the chat members and filter administrators and owners
    for member in chat_members:
        if (
            member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
            and not member.user.is_bot
        ):
            admins.append(member)

    if not admins:
        message.reply("No administrators or owners found in this chat.")
    else:
        response = "List of administrators and owners:\n"
        for admin in admins:
            response += (
                f"{admin.user.first_name} ({admin.user.id}) - Status: {admin.status}\n"
                f"Privileges:\n\n{admin.privileges}\n"
                f"Permissions:\n\n{admin.permissions}\n\n"
            )
        message.reply(response)
