from pyrogram import Client, filters, enums
from pyrogram.types import Message
from info import ADMINS


# Common function to list members with variations based on the filter
async def list_members_with_filter(client, message, filter_type, response_text):
    try:
        chat_id = message.chat.id

        # Check if the sender is the bot's admin
        if message.from_user.id in ADMINS:
            members = []
            async for member in client.get_chat_members(chat_id, filter=filter_type):
                # Extract member information
                member_info = f"Username: @{member.user.username}\n" \
                              f"User ID: {member.user.id}\n" \
                              f"First Name: {member.user.first_name}\n" \
                              f"Last Name: {member.user.last_name}"

                members.append(member_info)

            if members:
                # Send the list of members as a single message
                await message.reply(response_text.format('\n\n'.join(members)))
            else:
                await message.reply("There are no members that match the criteria in this group.")
        else:
            await message.reply("You are not authorized to use this command.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")

# Define a command filter to list administrators in the chat
@Client.on_message(filters.command("listadmins") & filters.group)
async def list_admins(client, message):
    await list_members_with_filter(
        client,
        message,
        enums.ChatMembersFilter.ADMINISTRATORS,
        "Admins in this group:\n{}"
    )

# Define a command handler for /members
@Client.on_message(filters.command("members") & filters.group)
async def list_all_members(client, message):
    await list_members_with_filter(
        client,
        message,
        enums.ChatMembersFilter.MEMBERS,
        "Members in this group:\n{}"
    )
    
