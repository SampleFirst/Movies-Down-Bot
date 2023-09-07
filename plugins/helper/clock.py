from pyrogram import Client, filters
import datetime

# Dictionary to keep track of live clock messages and tasks
live_clock_data = {}

# Function to send and update live clock
async def send_and_update_live_clock(chat_id, message_id):
    while True:
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        await client.edit_message_text(chat_id, message_id, f"Live Clock: {current_time}")
        await client.idle()  # Continuously update in real-time

# Define a command handler for /clock
@Client.on_message(filters.command("clock"))
async def show_live_clock(client, message):
    chat_id = message.chat.id

    # Check if the clock is already running in this chat
    if chat_id in live_clock_data:
        await message.reply("Live Clock is already running.")
    else:
        # Start the live clock in the chat and store the message ID
        live_message = await message.reply("Live Clock: Loading...")
        live_clock_data[chat_id] = live_message.message_id

        # Start the live clock update loop in the background
        asyncio.ensure_future(send_and_update_live_clock(chat_id, live_message.message_id))

# Define a command handler for /cancelclock
@Client.on_message(filters.command("cancelclock"))
async def cancel_live_clock(client, message):
    chat_id = message.chat.id

    # Check if the clock is running in this chat
    if chat_id in live_clock_data:
        # Stop the live clock by canceling the task and deleting the message
        task = asyncio.Task.all_tasks()
        for t in task:
            if hasattr(t, 'chat_id') and t.chat_id == chat_id:
                t.cancel()
        await client.delete_messages(chat_id, live_clock_data[chat_id])
        del live_clock_data[chat_id]
        await message.reply("Live Clock canceled.")
    else:
        await message.reply("Live Clock is not running in this chat.")
