import os
import re
import logging

from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from database.ia_filterdb import Media
from database.users_chats_db import db
from info import ADMINS, LOG_CHANNEL

from Script import script

logger = logging.getLogger(__name__)

RESULTS_PER_PAGE = 10

@Client.on_message(filters.command(['findfiles']) & filters.user(ADMINS))
async def handle_find_files(client, message):
    """Find files in the database based on search criteria"""
    search_query = " ".join(message.command[1:])  # Extract the search query from the command

    if not search_query:
        return await message.reply('✨ Please provide a name.\n\nExample: /findfiles Kantara.', quote=True)

    # Build the MongoDB query to search for files
    query = {
        'file_name': {"$regex": f".*{re.escape(search_query)}.*", "$options": "i"}
    }

    # Fetch the matching files from the database
    results = await Media.collection.find(query).to_list(length=None)

    if len(results) > 0:
        confirmation_message = f'✨ {len(results)} files found matching the search query "{search_query}" in the database:\n\n'
        starting_query = {
            'file_name': {"$regex": f"^{re.escape(search_query)}", "$options": "i"}
        }
        starting_results = await Media.collection.find(starting_query).to_list(length=None)
        confirmation_message += f'✨ {len(starting_results)} files found starting with "{search_query}" in the database.\n\n'
        confirmation_message += '✨ Please select the option for easier searching:'

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🌟 Find Related", callback_data=f"related_files:1:{search_query}"),
                    InlineKeyboardButton("🌟 Find Starting", callback_data=f"starting_files:1:{search_query}")
                ],
                [
                    InlineKeyboardButton("🗑️ Delete Related", callback_data=f"confirm_delete_related:{search_query}"),
                    InlineKeyboardButton("🗑️ Delete Starting", callback_data=f"confirm_delete_starting:{search_query}")
                ],
                [
                    InlineKeyboardButton("❌ Cancel", callback_data="manage:cancel")
                ]
            ]
        )
        await message.reply_text(confirmation_message, reply_markup=keyboard)
    else:
        await message.reply('❌ No files found matching the search query.', quote=True)

@Client.on_callback_query(filters.regex('^related_files'))
async def find_related_files(client, callback_query):
    data = callback_query.data.split(":")
    page = int(data[1])
    search_query = data[2]
    query = {
        'file_name': {"$regex": f".*{re.escape(search_query)}.*", "$options": "i"}
    }
    results = await Media.collection.find(query).to_list(length=None)

    total_results = len(results)
    num_pages = total_results // RESULTS_PER_PAGE + 1

    start_index = (page - 1) * RESULTS_PER_PAGE
    end_index = start_index + RESULTS_PER_PAGE
    current_results = results[start_index:end_index]

    result_message = f'{len(current_results)} files found with related names to "{search_query}" in the database:\n\n'
    for result in current_results:
        result_message += f'File Name: {result["file_name"]}\n'
        result_message += f'File Size: {result["file_size"]}\n\n'

    buttons = []

    if page > 1:
        buttons.append(InlineKeyboardButton("⬅️ Back", callback_data=f"related_files:{page-1}:{search_query}"))

    if page < num_pages:
        buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"related_files:{page+1}:{search_query}"))

    buttons.append(InlineKeyboardButton("🔚 Cancel", callback_data="cancel_find"))

    # Create button groups with two buttons each
    button_groups = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    keyboard = InlineKeyboardMarkup(button_groups)

    await callback_query.message.edit_text(result_message, reply_markup=keyboard)
    await callback_query.answer()


@Client.on_callback_query(filters.regex('^starting_files'))
async def find_starting_files(client, callback_query):
    data = callback_query.data.split(":")
    page = int(data[1])
    search_query = data[2]
    query = {
        'file_name': {"$regex": f"^{re.escape(search_query)}", "$options": "i"}
    }
    results = await Media.collection.find(query).to_list(length=None)

    total_results = len(results)
    num_pages = total_results // RESULTS_PER_PAGE + 1

    start_index = (page - 1) * RESULTS_PER_PAGE
    end_index = start_index + RESULTS_PER_PAGE
    current_results = results[start_index:end_index]

    result_message = f'{len(current_results)} files found with names starting "{search_query}" in the database:\n\n'
    for result in current_results:
        result_message += f'File Name: {result["file_name"]}\n'
        result_message += f'File Size: {result["file_size"]}\n\n'

    buttons = []

    if page > 1:
        buttons.append(InlineKeyboardButton("⬅️ Back", callback_data=f"related_files:{page-1}:{search_query}"))

    if page < num_pages:
        buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"related_files:{page+1}:{search_query}"))

    buttons.append(InlineKeyboardButton("🔚 Cancel", callback_data=f"cancel_find"))

    # Create button groups with two buttons each
    button_groups = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    keyboard = InlineKeyboardMarkup(button_groups)

    await callback_query.message.edit_text(result_message, reply_markup=keyboard)
    await callback_query.answer()

@Client.on_callback_query(filters.regex('^delete_related'))
async def delete_related_files(client, callback_query):
    file_name = callback_query.data.split(":", 1)[1]
    result = await Media.collection.delete_many({
        'file_name': {"$regex": f".*{re.escape(file_name)}.*", "$options": "i"}
    })

    if result.deleted_count:
        message_text = f"✅ Deleted {result.deleted_count} files."
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🏠 Home", callback_data="deletename"),
                    InlineKeyboardButton("⬅️ Back", callback_data=f"confirm_delete_related:{file_name}")
                ],
                [
                    InlineKeyboardButton("🔚 Cancel", callback_data="cancel_delete")
                ]
            ]
        )
    else:
        message_text = "❌ Deletion failed. No files deleted."
        keyboard = InlineKeyboardMarkup(
            [
                [
@Client.on_message(filters.command(['findfiles']) & filters.user(ADMINS))
async def handle_find_files(client, message):
    """Find files in the database based on search criteria"""
    search_query = " ".join(message.command[1:])  # Extract the search query from the command

    if not search_query:
        return await message.reply('✨ Please provide a name.\n\nExample: /findfiles Kantara.', quote=True)

    # Build the MongoDB query to search for files
    query = {
        'file_name': {"$regex": f".*{re.escape(search_query)}.*", "$options": "i"}
    }

    # Fetch the matching files from the database
    results = await Media.collection.find(query).to_list(length=None)

    if len(results) > 0:
        confirmation_message = f'✨ {len(results)} files found matching the search query "{search_query}" in the database:\n\n'
        starting_query = {
            'file_name': {"$regex": f"^{re.escape(search_query)}", "$options": "i"}
        }
        starting_results = await Media.collection.find(starting_query).to_list(length=None)
        confirmation_message += f'✨ {len(starting_results)} files found starting with "{search_query}" in the database.\n\n'
        confirmation_message += '✨ Please select the option for easier searching:'

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🌟 Find Related", callback_data=f"related_files:1:{search_query}"),
                    InlineKeyboardButton("🌟 Find Starting", callback_data=f"starting_files:1:{search_query}")
                ],
                [
                    InlineKeyboardButton("🗑️ Delete Related", callback_data=f"confirm_delete_related:{search_query}"),
                    InlineKeyboardButton("🗑️ Delete Starting", callback_data=f"confirm_delete_starting:{search_query}")
                ],
                [
                    InlineKeyboardButton("❌ Cancel", callback_data="manage:cancel")
                ]
            ]
        )
        await message.reply_text(confirmation_message, reply_markup=keyboard)
    else:
        await message.reply('❌ No files found matching the search query.', quote=True)
        


@Client.on_callback_query(filters.regex('^related_files'))
async def find_related_files(client, callback_query):
    data = callback_query.data.split(":")
    page = int(data[1])
    search_query = data[2]
    query = {
        'file_name': {"$regex": f".*{re.escape(search_query)}.*", "$options": "i"}
    }
    results = await Media.collection.find(query).to_list(length=None)

    total_results = len(results)
    num_pages = total_results // RESULTS_PER_PAGE + 1

    start_index = (page - 1) * RESULTS_PER_PAGE
    end_index = start_index + RESULTS_PER_PAGE
    current_results = results[start_index:end_index]

    result_message = f'{len(current_results)} files found with related names to "{search_query}" in the database:\n\n'
    for result in current_results:
        result_message += f'File Name: {result["file_name"]}\n'
        result_message += f'File Size: {result["file_size"]}\n\n'

    buttons = []

    if page > 1:
        buttons.append(InlineKeyboardButton("⬅️ Back", callback_data=f"related_files:{page-1}:{search_query}"))

    if page < num_pages:
        buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"related_files:{page+1}:{search_query}"))

    buttons.append(InlineKeyboardButton("🔚 Cancel", callback_data="cancel_find"))

    # Create button groups with two buttons each
    button_groups = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    keyboard = InlineKeyboardMarkup(button_groups)

    await callback_query.message.edit_text(result_message, reply_markup=keyboard)
    await callback_query.answer()


@Client.on_callback_query(filters.regex('^starting_files'))
async def find_starting_files(client, callback_query):
    data = callback_query.data.split(":")
    page = int(data[1])
    search_query = data[2]
    query = {
        'file_name': {"$regex": f"^{re.escape(search_query)}", "$options": "i"}
    }
    results = await Media.collection.find(query).to_list(length=None)

    total_results = len(results)
    num_pages = total_results // RESULTS_PER_PAGE + 1

    start_index = (page - 1) * RESULTS_PER_PAGE
    end_index = start_index + RESULTS_PER_PAGE
    current_results = results[start_index:end_index]

    result_message = f'{len(current_results)} files found with names starting "{search_query}" in the database:\n\n'
    for result in current_results:
        result_message += f'File Name: {result["file_name"]}\n'
        result_message += f'File Size: {result["file_size"]}\n\n'

    buttons = []

    if page > 1:
        buttons.append(InlineKeyboardButton("⬅️ Back", callback_data=f"related_files:{page-1}:{search_query}"))

    if page < num_pages:
        buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"related_files:{page+1}:{search_query}"))

    buttons.append(InlineKeyboardButton("🔚 Cancel", callback_data=f"cancel_find"))

    # Create button groups with two buttons each
    button_groups = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    keyboard = InlineKeyboardMarkup(button_groups)

    await callback_query.message.edit_text(result_message, reply_markup=keyboard)
    await callback_query.answer()




@Client.on_callback_query(filters.regex('^delete_related'))
async def delete_related_files(client, callback_query):
    file_name = callback_query.data.split(":", 1)[1]
    result = await Media.collection.delete_many({
        'file_name': {"$regex": f".*{re.escape(file_name)}.*", "$options": "i"}
    })

    if result.deleted_count:
        message_text = f"✅ Deleted {result.deleted_count} files."
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🏠 Home", callback_data="deletename"),
                    InlineKeyboardButton("⬅️ Back", callback_data=f"confirm_delete_related:{file_name}")
                ],
                [
                    InlineKeyboardButton("🔚 Cancel", callback_data="cancel_delete")
                ]
            ]
        )
    else:
        message_text = "❌ Deletion failed. No files deleted."
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🏠 Home", callback_data="deletename"),
                    InlineKeyboardButton("⬅️ Back", callback_data=f"confirm_delete_related:{file_name}")
                ],
                [
                    InlineKeyboardButton("🔚 Cancel", callback_data="cancel_delete")
                ]
            ]
        )

    await callback_query.message.edit_text(message_text, reply_markup=keyboard)

@Client.on_callback_query(filters.regex('^confirm_delete_related'))
async def confirm_delete_related_files(client, callback_query):
    file_name = callback_query.data.split(":", 1)[1]
    confirmation_message = f'⚠️ Are you sure you want to delete all files with the name "{file_name}"?\n\n' \
                           f'This action cannot be undone.'

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ Yes", callback_data=f"delete_related:{file_name}"),
                InlineKeyboardButton("🏠 Home", callback_data="deletename")
            ],
            [
                InlineKeyboardButton("🔚 Cancel", callback_data="cancel_delete")
            ]
        ]
    )

    await callback_query.message.edit_text(confirmation_message, reply_markup=keyboard)


@Client.on_callback_query(filters.regex('^delete_starting'))
async def delete_starting_files(client, callback_query):
    file_name = callback_query.data.split(":", 1)[1]
    result = await Media.collection.delete_many({
        'file_name': {"$regex": f"^{re.escape(file_name)}", "$options": "i"}
    })

    if result.deleted_count:
        message_text = f"✅ Deleted {result.deleted_count} files."
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🏠 Home", callback_data="deletename"),
                    InlineKeyboardButton("⬅️ Back", callback_data=f"confirm_delete_starting:{file_name}")
                ],
                [
                    InlineKeyboardButton("🔚 Cancel", callback_data="cancel_delete")
                ]
            ]
        )
    else:
        message_text = "❌ Deletion failed. No files deleted."
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🏠 Home", callback_data="deletename"),
                    InlineKeyboardButton("⬅️ Back", callback_data=f"confirm_delete_starting:{file_name}")
                ],
                [
                    InlineKeyboardButton("🔚 Cancel", callback_data="cancel_delete")
                ]
            ]
        )

    await callback_query.message.edit_text(message_text, reply_markup=keyboard)
    

@Client.on_callback_query(filters.regex('^confirm_delete_starting'))
async def confirm_delete_starting_files(client, callback_query):
    file_name = callback_query.data.split(":", 1)[1]
    confirmation_message = f'⚠️ Are you sure you want to delete all files with names starting "{file_name}"?\n\n' \
                           f'This action cannot be undone.'

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ Yes", callback_data=f"delete_starting:{file_name}"),
                InlineKeyboardButton("🏠 Home", callback_data="deletename")
            ],
            [
                InlineKeyboardButton("🔚 Cancel", callback_data="cancel_delete")
            ]
        ]
    )

    await callback_query.message.edit_text(confirmation_message, reply_markup=keyboard)

