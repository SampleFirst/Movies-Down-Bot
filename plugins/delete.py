# Standard Library Imports
import asyncio
import logging

# Third-Party Library Imports
import pyrogram
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram import Client, filters, enums

# Database Imports
from database.users_chats_db import db
from database.ia_filterdb import Media, get_bad_files

# Environment Variables
from info import ADMINS
    
# Logging Configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

# Global Variables
back_stack = []


@Client.on_message(filters.command("deletefiles") & filters.user(ADMINS))
async def deletemultiplefiles(bot, message):
    btn = [
        [
            InlineKeyboardButton("Delete PreDVDs", callback_data="predvd"),
            InlineKeyboardButton("Delete CamRips", callback_data="camrip")
        ],
        [
            InlineKeyboardButton("Delete HDCams", callback_data="hdcam"),
            InlineKeyboardButton("Delete S-Prints", callback_data="s-print")
        ],
        [
            InlineKeyboardButton("Delete HDTVRip", callback_data="hdtvrip"),
            InlineKeyboardButton("Delete Cancel", callback_data="cancel_delete")
        ]
    ]
    await message.reply_text(
        text="<b>Select the type of files you want to delete!\n\nThis will delete 100 files from the database for the selected type.</b>",
        reply_markup=InlineKeyboardMarkup(btn),
        quote=True
    )
    
@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    data = query.data

    if query.data == "predvd":
        files, next_offset, total = await get_bad_files('predvd', offset=0)
        if total > 0:
            confirm_btns = [
                [
                    InlineKeyboardButton("☑️ Confirm Deletion", callback_data="confirm_delete predvd"),
                    InlineKeyboardButton("❎Cancel", callback_data="cancel_deletefiles")
                ],
                [
                    InlineKeyboardButton("🏠 Home", callback_data="deletefiles")
                ]
            ]
            await query.message.edit_text(
                f"<b>✨ {total} PreDVD files detected. Are you sure you want to delete them?</b>",
                reply_markup=InlineKeyboardMarkup(confirm_btns)
            )
            # Save the current page to the back stack
            back_stack.append({
                'text': query.message.caption or query.message.text,
                'reply_markup': query.message.reply_markup
            })
        else:
            # Add buttons for going back and canceling
            btn = [
                [
                    InlineKeyboardButton("🔙 Back", callback_data="deletefiles"),
                    InlineKeyboardButton("❎ Cancel", callback_data="cancel_deletefiles")
                ]
            ]
            await query.message.edit_text(
                "<b>❎ No PreDVD files found for deletion.</b>",
                reply_markup=InlineKeyboardMarkup(btn)
            )

    elif query.data == "camrip":
        files, next_offset, total = await get_bad_files('camrip', offset=0)
        if total > 0:
            confirm_btns = [
                [
                    InlineKeyboardButton("☑️ Confirm Deletion", callback_data="confirm_delete camrip"),
                    InlineKeyboardButton("❎ Cancel", callback_data="cancel_deletefiles")
                ],
                [
                    InlineKeyboardButton("🏠 Home", callback_data="deletefiles")
                ]
            ]
            await query.message.edit_text(
                f"<b>✨ {total} CamRip files detected. Are you sure you want to delete them?</b>",
                reply_markup=InlineKeyboardMarkup(confirm_btns)
            )
            # Save the current page to the back stack
            back_stack.append({
                'text': query.message.caption or query.message.text,
                'reply_markup': query.message.reply_markup
            })
        else:
            # Add buttons for going back and canceling
            btn = [
                [
                    InlineKeyboardButton("🔙 Back", callback_data="deletefiles"),
                    InlineKeyboardButton("❎ Cancel", callback_data="cancel_deletefiles")
                ]
            ]
            await query.message.edit_text(
                "<b>❎ No CamRip files found for deletion.</b>",
                reply_markup=InlineKeyboardMarkup(btn)
            )

    elif query.data == "hdcam":
        files, next_offset, total = await get_bad_files('hdcam', offset=0)
        if total > 0:
            confirm_btns = [
                [
                    InlineKeyboardButton("☑️ Confirm Deletion", callback_data="confirm_delete hdcam"),
                    InlineKeyboardButton("❎ Cancel", callback_data="cancel_deletefiles")
                ],
                [
                    InlineKeyboardButton("🏠 Home", callback_data="deletefiles")
                ]
            ]
            await query.message.edit_text(
                f"<b>✨ {total} HDCam files detected. Are you sure you want to delete them?</b>",
                reply_markup=InlineKeyboardMarkup(confirm_btns)
            )
            # Save the current page to the back stack
            back_stack.append({
                'text': query.message.caption or query.message.text,
                'reply_markup': query.message.reply_markup
            })
        else:
            # Add buttons for going back and canceling
            btn = [
                [
                    InlineKeyboardButton("🔙 Back", callback_data="deletefiles"),
                    InlineKeyboardButton("❎ Cancel", callback_data="cancel_deletefiles")
                ]
            ]
            await query.message.edit_text(
                "<b>❎ No HDCam files found for deletion.</b>",
                reply_markup=InlineKeyboardMarkup(btn)
            )

    elif query.data == "s-print":
        files, next_offset, total = await get_bad_files('s-print', offset=0)
        if total > 0:
            confirm_btns = [
                [
                    InlineKeyboardButton("☑️ Confirm Deletion", callback_data="confirm_delete s-print"),
                    InlineKeyboardButton("❎ Cancel", callback_data="cancel_deletefiles")
                ],
                [
                    InlineKeyboardButton("🏠 Home", callback_data="deletefiles")
                ]
            ]
            await query.message.edit_text(
                f"<b>✨ {total} S-Print files detected. Are you sure you want to delete them?</b>",
                reply_markup=InlineKeyboardMarkup(confirm_btns)
            )
            # Save the current page to the back stack
            back_stack.append({
                'text': query.message.caption or query.message.text,
                'reply_markup': query.message.reply_markup
            })
        else:
            # Add buttons for going back and canceling
            btn = [
                [
                    InlineKeyboardButton("🔙 Back", callback_data="deletefiles"),
                    InlineKeyboardButton("❎ Cancel", callback_data="cancel_deletefiles")
                ]
            ]
            await query.message.edit_text(
                "<b>❎ No S-Print files found for deletion.</b>",
                reply_markup=InlineKeyboardMarkup(btn)
            )
    
    elif query.data == "hdtvrip":
        files, next_offset, total = await get_bad_files('hdtvrip', offset=0)
        if total > 0:
            confirm_btns = [
                [
                    InlineKeyboardButton("☑️ Confirm Deletion", callback_data="confirm_delete hdtvrip"),
                    InlineKeyboardButton("❎ Cancel", callback_data="cancel_deletefiles")
                ],
                [
                    InlineKeyboardButton("🏠 Home", callback_data="deletefiles")
                ]
            ]
            await query.message.edit_text(
                f"<b>✨ {total} HDTVrip files detected. Are you sure you want to delete them?</b>",
                reply_markup=InlineKeyboardMarkup(confirm_btns)
            )
            # Save the current page to the back stack
            back_stack.append({
                'text': query.message.caption or query.message.text,
                'reply_markup': query.message.reply_markup
            })
        else:
            # Add buttons for going back and canceling
            btn = [
                [
                    InlineKeyboardButton("🔙 Back", callback_data="deletefiles"),
                    InlineKeyboardButton("❎ Cancel", callback_data="cancel_deletefiles")
                ]
            ]
            await query.message.edit_text(
                "<b>❎ No HDTVrip files found for deletion.</b>",
                reply_markup=InlineKeyboardMarkup(btn)
            )
   
    elif query.data.startswith("confirm_delete"):
        file_type = query.data.split()[1]
        files, next_offset, total = await get_bad_files(file_type, offset=0)
        deleted = 0
        for file in files:
            file_ids = file.file_id
            result = await Media.collection.delete_one({'_id': file_ids})
            if result.deleted_count:
                logger.info(f'{file_type} File Found! Successfully deleted from the database.')
            deleted += 1
        deleted = str(deleted)
        await query.message.edit_text(f"<b>Successfully deleted {deleted} {file_type.capitalize()} files.</b>")

        # Add buttons for canceling and going back
        btn = [
            [
                InlineKeyboardButton("❎ Cancel", callback_data="cancel_deletefiles"),
            ],
            [
                InlineKeyboardButton("🏠 Back", callback_data="deletefiles"),
            ]
        ]
        await query.message.edit_text(
            text=f"<b>Successfully deleted {deleted} {file_type.capitalize()} files.</b>",
            reply_markup=InlineKeyboardMarkup(btn)
        )

    elif query.data == "deletefiles":
        # Check if there are any pages in the back stack
        if back_stack:
            previous_page = back_stack.pop()
            await query.message.edit_text(
                previous_page['text'],
                reply_markup=previous_page['reply_markup']
            )
        else:
            # If no previous page, remove the back button and show the original command page
            btn = [
                [
                    InlineKeyboardButton("Delete PreDVDs", callback_data="predvd"),
                    InlineKeyboardButton("Delete CamRips", callback_data="camrip")
                ],
                [
                    InlineKeyboardButton("Delete HDCams", callback_data="hdcam"),
                    InlineKeyboardButton("Delete S-Prints", callback_data="s-print")
                ],
                [
                    InlineKeyboardButton("Delete HDTVRip", callback_data="hdtvrip"),
                    InlineKeyboardButton("Cancel", callback_data="cancel_deletefiles")
                ]
            ]
            await query.message.edit_text(
                "<b>✨ Select the type of files you want to delete!\n\n✨ This will delete 100 files from the database for the selected type.</b>",
                reply_markup=InlineKeyboardMarkup(btn)
            )
            
    elif query.data == "cancel_deletefiles":
        await query.message.reply_text("<b>☑️ File deletion canceled.</b>")
