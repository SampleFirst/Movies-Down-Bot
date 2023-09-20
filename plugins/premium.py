from pyrogram import Client, filters
from datetime import datetime, timedelta
from database.users_chats_db import db
from info import ADMINS 

@Client.on_message(filters.command("addpremium") & filters.user(ADMINS))
async def add_premium_user(bot, message):
    try:
        # Parse the user ID from the command arguments
        user_id = int(message.command[1])
        
        # Check if the user already exists in the database as a premium user
        if await db.check_premium_status(user_id):
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

@Client.on_message(filters.command("checkpremium"))
async def check_premium_status(bot, message):
    try:
        # Parse the user ID from the command arguments
        user_id = int(message.command[1])

        # Check the premium status of the user
        is_premium = await db.check_premium_status(user_id)
        
        if is_premium:
            await message.reply("User is a premium user.")
        else:
            await message.reply("User is not a premium user.")
    
    except (IndexError, ValueError):
        await message.reply("Invalid command usage. Use /checkpremium <user_id>")

@Client.on_message(filters.command("removepremium") & filters.user(ADMINS))
async def remove_premium_user(bot, message):
    try:
        # Parse the user ID from the command arguments
        user_id = int(message.command[1])
        
        # Check if the user exists as a premium user in the database
        if await db.check_premium_status(user_id):
            # Remove the user from premium status in the database
            await db.remove_premium_user(user_id)
            await message.reply("User has been removed from premium status.")
        else:
            await message.reply("User is not a premium user.")
    
    except (IndexError, ValueError):
        await message.reply("Invalid command usage. Use /removepremium <user_id>")

@Client.on_message(filters.command("checkmypremium"))
async def check_my_premium_status(bot, message):
    try:
        # Get the user's own ID
        user_id = message.from_user.id

        # Check the premium status of the user
        is_premium = await db.check_premium_status(user_id)
        
        if is_premium:
            await message.reply("You are a premium user.")
        else:
            await message.reply("You are not a premium user.")
    
    except Exception as e:
        print(e)
        await message.reply("An error occurred while checking your premium status.")

@Client.on_message(filters.command("premium_users") & filters.user(ADMINS))
async def premium_users_command(bot, message):
    try:
        premium_users = await db.get_all_premium_users().to_list(length=None)
        if not premium_users:
            await message.reply("No premium users found.")
            return

        response_text = "Premium Users List:\n\n"
        for user in premium_users:
            user_id = user["id"]
            user_name = user["name"]
            premium_start_date = user["premium_status"]["start_date"]
            premium_end_date = user["premium_status"]["end_date"]

            response_text += f"User ID: {user_id}\n"
            response_text += f"User Name: {user_name}\n"
            response_text += f"Premium Start Date: {premium_start_date}\n"
            response_text += f"Premium End Date: {premium_end_date}\n\n"

        await message.reply(response_text)
    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}")
