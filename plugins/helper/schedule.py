from pyrogram import Client, filters
from datetime import datetime, timedelta
import asyncio


# Define a command handler
@Client.on_message(filters.command(["schedule"]))
async def schedule_message(client, message):
    try:
        # Create a message indicating it's a scheduled message
        scheduled_message = "This is a scheduled message."

        # Parse the date and time for scheduling
        schedule_date = datetime.strptime(message.text.split(" ", 1)[1], "%Y-%m-%d %H:%M:%S")

        # Calculate the time difference to schedule the message
        time_until_schedule = schedule_date - datetime.now(datetime.timezone.utc)

        if time_until_schedule.total_seconds() < 0:
            await message.reply("The scheduled time has already passed.")
            return

        # Use the send_message function with delay to schedule the message
        await message.reply(f"Scheduling message for {schedule_date.strftime('%Y-%m-%d %H:%M:%S')} UTC...")
        await asyncio.sleep(time_until_schedule.total_seconds())
        await client.send_message(
            chat_id=message.chat.id,
            text=scheduled_message
        )
        await message.reply("Message scheduled successfully!")

    except (ValueError, Exception) as e:
        await message.reply(f"An error occurred: {str(e)}")
