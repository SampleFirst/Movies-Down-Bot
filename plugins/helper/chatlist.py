from pyrogram import Client, filters, enums
from pyrogram.types import Message
from info import ADMINS


# Define the command handler function
@Client.on_message(filters.command('list_chats') & filters.user(ADMINS))
def list_admin_chats(client, message: Message):
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


# Define a command handler for /admins
@Client.on_message(filters.command("listadmins") & filters.group)
async def list_admins(client, message):
    try:
        chat_id = message.chat.id

        # Check if the sender is the bot's admin
        if message.from_user.id in ADMINS:
            # Get and list administrators in the chat
            admins = []
            async for member in client.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
                admins.append(member.user.first_name)

            if admins:
                # Send the list of administrators as a single message
                await message.reply(f"Admins in this group: {', '.join(admins)}")
            else:
                await message.reply("There are no administrators in this group.")
        else:
            await message.reply("You are not authorized to use this command.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")

# Define a command handler for /members
@Client.on_message(filters.command("members") & filters.group)
async def list_members(client, message):
    try:
        chat_id = message.chat.id

        # Check if the sender is the bot's admin
        if message.from_user.id in ADMINS:
            members = await client.get_chat_members(chat_id)
            member_list = [member.user.first_name for member in members]
            await message.reply(f"Members in this group: {', '.join(member_list)}")
        else:
            await message.reply("You are not authorized to use this command.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")


# Define a command handler for /deletehistory
@Client.on_message(filters.command("deletehistory") & filters.group & filters.user("ADMINS"))
def delete_history(client, message):
    chat_id = message.chat.id
    client.delete_history(chat_id)
    client.send_message(chat_id, "Chat history has been deleted.")

# Define a command filter to trigger the command in a private chat
@Client.on_message(filters.command("getprivileges") & filters.user(ADMINS))
async def get_privileges_cmd(client, message):
    # Get the chat ID
    chat_id = message.chat.id

    # Get the bot's default privileges for the chat
    privileges = await client.get_bot_default_privileges(for_channels=False)  # Change to True for channels

    if privileges:
        # Send the privileges as a message
        await client.send_message(chat_id, f"Bot Privileges in this chat:\n{privileges}")
    else:
        await client.send_message(chat_id, "Bot privileges not found for this chat.")
