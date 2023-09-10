from pyrogram import Client, filters, enums
from pyrogram.types import Message
from info import ADMINS


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


@Client.on_message(filters.command("memberslist") & filters.group)
async def list_members(client, message):
    try:
        chat_id = message.chat.id

        # Check if the sender is the bot's admin
        if message.from_user.id in ADMINS:
            members_info = []
            async for member in client.get_chat_members(chat_id):
                user = member.user
                member_info = f"Username: @{member.user.username}\n" \
                              f"User ID: {member.user.id}\n" \
                              f"First Name: {member.user.first_name}\n" \
                              f"Last Name: {member.user.last_name}"
    
                members_info.append(member_info)
            
            members_list_text = "\n\n".join(members_info)
            await message.reply(f"Members in this group:\n{members_list_text}")
        else:
            await message.reply("You are not authorized to use this command.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")

# Define a command filter to list administrators in the chat
@Client.on_message(filters.command("adminslist") & filters.group)
async def list_admins(client, message):
    await list_members_with_filter(
        client,
        message,
        enums.ChatMembersFilter.ADMINISTRATORS,
        "Admins in this group:\n{}"
    )

# Define a command filter to list banned members in the chat
@Client.on_message(filters.command("banlist") & filters.group)
async def list_all_bans(client, message):
    await list_members_with_filter(
        client,
        message,
        enums.ChatMembersFilter.BANNED,
        "Banned members in this group:\n{}"
    )

# Define a command filter to list bots in the chat
@Client.on_message(filters.command("botslist") & filters.group)
async def list_all_bots(client, message):
    await list_members_with_filter(
        client,
        message,
        enums.ChatMembersFilter.BOTS,
        "Bots in this group:\n{}"
    )

# Define a command filter to list recent members in the chat
@Client.on_message(filters.command("recentslist") & filters.group)
async def list_all_recent(client, message):
    await list_members_with_filter(
        client,
        message,
        enums.ChatMembersFilter.RECENT,
        "Recent members in this group:\n{}"
    )

# Define a function to handle the /is command
@Client.on_message(filters.command("is"))
async def is_command(client, message):
    # Get a list of all the chats where the bot is a member
    async for chat in client.get_dialogs():
        # Initialize variables to count the types of chats
        supergroups = 0
        groups = 0
        channels = 0

        if chat.chat.type == "supergroup":
            supergroups += 1
        elif chat.chat.type == "group":
            groups += 1
        elif chat.chat.type == "channel":
            channels += 1

    # Compose the response message
    response = f"Supergroups: {supergroups}\nGroups: {groups}\nChannels: {channels}"

    # Send the response back to the user
    await message.reply(response)
    

@Client.on_message(filters.command("list_chats"))
async def list_chats_categories(client, message):
    # Split the message into words
    words = message.text.split()

    # Check if there are enough words in the message
    if len(words) < 2:
        await message.reply("Usage: /list_chats [category]")
        return

    category = words[1].lower()  # Extract the category from the command
    chats = []

    if category == "groups":
        chats = await client.get_dialogs(filters=Client.FILTERS_GROUP)
    elif category == "supergroups":
        chats = await client.get_dialogs(filters=Client.FILTERS_SUPERGROUPS)
    elif category == "channels":
        chats = await client.get_dialogs(filters=Client.FILTERS_CHANNELS)

    chat_list = "\n".join([f"{chat.chat.id} - {chat.chat.title}" for chat in chats])

    await message.reply(f"List of {category.capitalize()}:\n{chat_list}")
