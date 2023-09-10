from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from info import ADMINS

@Client.on_message(filters.command("admincommands") & filters.user(ADMINS))
async def send_commands_list(client, message: Message):
    # Create buttons for different command categories
    buttons = [
        [
            InlineKeyboardButton("Bot Commands", callback_data="bot_commands"),
            InlineKeyboardButton("Group Management Commands", callback_data="group_commands"),
        ],
        [
            InlineKeyboardButton("Timepass Commands", callback_data="timepass_commands"),
            InlineKeyboardButton("Extra Features Commands", callback_data="extra_commands"),
        ],
        [
            InlineKeyboardButton("Cancel", callback_data="cancel")
        ],
    ]

    # Create an InlineKeyboardMarkup with the buttons
    markup = InlineKeyboardMarkup(buttons)

    # Send a message with the buttons
    await message.reply_text("Please choose a category of commands:", reply_markup=markup)


# Define callback handlers for category buttons
@Client.on_callback_query(filters.regex("^bot_commands$"))
async def bot_commands_callback(client, callback_query):
    bot_commands_text = """
    Bot Commands:
    /logs - Get recent errors
    /stats - Get the status of files in the database.
    /filter - Add manual filters
    # Add more bot commands here
    """

    keyboard = [
        [
            InlineKeyboardButton("Cancel", callback_data="cancel"),
            InlineKeyboardButton("Back", callback_data="back")
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await callback_query.answer()
    await callback_query.message.edit_text(bot_commands_text, reply_markup=reply_markup)


@Client.on_callback_query(filters.regex("^group_commands$"))
async def group_commands_callback(client, callback_query):
    group_commands_text = """
    Group Management Commands:
    /promote - Promote a member to admin
    /demote - Demote an admin to a member
    /kick - Kick a member from the group
    /ban - Ban a member from the group
    /unban - Unban a previously banned member
    # Add more group management commands here
    """

    keyboard = [
        [
            InlineKeyboardButton("Cancel", callback_data="cancel"),
            InlineKeyboardButton("Back", callback_data="back")
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await callback_query.answer()
    await callback_query.message.edit_text(group_commands_text, reply_markup=reply_markup)


@Client.on_callback_query(filters.regex("^timepass_commands$"))
async def timepass_commands_callback(client, callback_query):
    timepass_commands_text = """
    Timepass Commands:
    /font - Fonts for your text
    /song - Get a song
    /video - Get a video
    # Add more timepass commands here
    """

    keyboard = [
        [
            InlineKeyboardButton("Cancel", callback_data="cancel"),
            InlineKeyboardButton("Back", callback_data="back")
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await callback_query.answer()
    await callback_query.message.edit_text(timepass_commands_text, reply_markup=reply_markup)


@Client.on_callback_query(filters.regex("^extra_commands$"))
async def extra_commands_callback(client, callback_query):
    extra_commands_text = """
    Extra Features Commands:
    /connect - Connect to PM.
    /disconnect - Disconnect from PM
    /del - Delete a filter
    /delall - Delete all filters
    /deleteall - Delete all index (autofilter)
    /delete - Delete a specific file from the index.
    /info - Get user info
    /id - Get Telegram IDs.
    /imdb - Fetch info from IMDb.
    /users - Get a list of my users and IDs.
    /chats - Get a list of my chats and IDs.
    /broadcast - Broadcast a message to all Elsa users.
    /gfilter - Group filter
    /grp_broadcast - Broadcast to all groups
    /deletefiles - PreDvD CamRip deletion
    # Add more extra features commands here
    """

    keyboard = [
        [
            InlineKeyboardButton("Cancel", callback_data="cancel"),
            InlineKeyboardButton("Back", callback_data="back")
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await callback_query.answer()
    await callback_query.message.edit_text(extra_commands_text, reply_markup=reply_markup)


@Client.on_callback_query(filters.regex("^cancel$"))
async def cancel_callback(client, callback_query):
    await callback_query.answer("Cancelled")
    await callback_query.message.delete()


@Client.on_callback_query(filters.regex("^back$"))
async def back_commands_list(client, callback_query):
    # Create buttons for different command categories
    buttons = [
        [
            InlineKeyboardButton("Bot Commands", callback_data="bot_commands"),
            InlineKeyboardButton("Group Management Commands", callback_data="group_commands"),
        ],
        [
            InlineKeyboardButton("Timepass Commands", callback_data="timepass_commands"),
            InlineKeyboardButton("Extra Features Commands", callback_data="extra_commands"),
        ],
        [
            InlineKeyboardButton("Cancel", callback_data="cancel")
        ],
    ]

    # Create an InlineKeyboardMarkup with the buttons
    markup = InlineKeyboardMarkup(buttons)

    await callback_query.answer()
    await callback_query.message.edit_text("Please choose a category of commands:", reply_markup=markup)
