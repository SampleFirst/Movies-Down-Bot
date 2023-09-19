from pyrogram import Client, filters
from datetime import datetime, timedelta
from database.users_chats_db.py import db


@Client.on_message(filters.command("addpremium") filters.user(ADMINS))
async def add_premium_user(bot, message):
    try:
        # Parse the user ID from the command arguments
        user_id = int(message.command[1])
        
        # Check if the user already exists in the database as a premium user
        if await db.is_premium_user_exist(user_id):
            await message.reply("User is already a premium user.")
        else:
            # Calculate the start and end dates for the premium subscription (1 month duration)
            current_time = datetime.now()
            start_date = current_time
            end_date = current_time + timedelta(days=30)
            
            # Add the user as a premium user in the database
            await db.add_premium_user(user_id, message.from_user.first_name, start_date, end_date)
            
            await message.reply("User has been added as a premium user for 1 month.")
    
    except (IndexError, ValueError):
        await message.reply("Invalid command usage. Use /addpremium <user_id>")
