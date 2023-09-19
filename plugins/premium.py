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
            await db.update_premium_status(user_id, False)
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


@Client.on_message(filters.command("premium") filters.user(ADMINS))
async def add_premium_user_command(client, message):
    user_id = message.from_user.id
    user_name = message.from_user.username
    premium_start_date = datetime.now()
    premium_end_date = premium_start_date + timedelta(days=30)  # Example: Premium for 30 days
    await db.add_premium_user(user_id, user_name, premium_start_date, premium_end_date)
    await message.reply("You have been upgraded to Premium!")

# Command to check if a user is a premium user (Only for admins)
@Client.on_message(filters.command("seepremium") filters.user(ADMINS))
async def check_premium_user_command(client, message):
    user_id = message.from_user.id
    is_premium = await db.is_premium_user(user_id)
    if is_premium:
        await message.reply("You are a Premium user.")
    else:
        await message.reply("You are a Free user.")

# Command to demote a premium user to a free user (Only for admins)
@Client.on_message(filters.command("deletepremium") filters.user(ADMINS))
async def remove_premium_user_command(client, message):
    user_id = message.from_user.id
    await db.remove_premium_user(user_id)
    await message.reply("You have been demoted to a Free user!")

# Command to check your plan (Premium or Free)
@Client.on_message(filters.command("myplan") & filters.private)
async def check_user_plan_command(client, message):
    user_id = message.from_user.id
    user_plan = await db.get_user_plan(user_id)
    await message.reply(f"Your plan is: {user_plan}")
    
