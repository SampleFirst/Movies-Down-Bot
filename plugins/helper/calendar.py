import calendar
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import CallbackQuery



@Client.on_message(filters.command("calendar"))
async def show_calendar(client, message):
    try:
        # Parse the input message for year and month
        text = message.text.split()
        if len(text) != 3:
            await message.reply_text("Please use the /calendar command followed by year and month (e.g., /calendar 2023 12).")
            return

        _, year, month = text
        year = int(year)
        month = int(month)

        # Create a calendar for the specified year and month
        cal = calendar.month(year, month)

        # Create an inline keyboard for navigation
        prev_month = month - 1 if month > 1 else 12
        prev_year = year if month > 1 else year - 1
        next_month = month + 1 if month < 12 else 1
        next_year = year if month < 12 else year + 1

        keyboard = [
            [
                InlineKeyboardButton("Previous", callback_data=f"prev {prev_year} {prev_month}"),
                InlineKeyboardButton("Next", callback_data=f"next {next_year} {next_month}"),
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        # Send the calendar with navigation buttons
        await message.reply_text(cal, reply_markup=reply_markup)

    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")

@Client.on_callback_query(filters.regex(r"prev|next"))
async def update_calendar(client, callback_query: CallbackQuery):
    data = callback_query.data.split()
    action, year, month = data

    year = int(year)
    month = int(month)

    if action == "prev":
        month -= 1
        if month < 1:
            month = 12
            year -= 1
    else:
        month += 1
        if month > 12:
            month = 1
            year += 1

    # Create a new calendar for the updated year and month
    cal = calendar.month(year, month)

    keyboard = [
        [
            InlineKeyboardButton("Previous", callback_data=f"prev {year} {month}"),
            InlineKeyboardButton("Next", callback_data=f"next {year} {month}"),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Edit the message with the updated calendar and navigation buttons
    await callback_query.edit_message_text(cal, reply_markup=reply_markup)
