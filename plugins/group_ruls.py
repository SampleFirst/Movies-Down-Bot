from pyrogram import Client, filters
from pyrogram.types import Message
from info import LOG_CHANNEL

# Dictionary to store chat settings (on/off)
chat_settings = {}

# Command to toggle the feature on/off
@Client.on_message(filters.command("ruls") & filters.group)
def toggle_ruls_command(client, message):
    chat_id = message.chat.id

    if len(message.command) < 2:
        message.reply("Usage: /ruls [on|off]")
        return

    setting = message.command[1].lower()
    
    if setting not in ["on", "off"]:
        message.reply("Usage: /ruls [on|off]")
        return

    chat_settings[chat_id] = setting
    message.reply(f"Ruls feature is now {setting}")

# Filter for detecting messages in a group
@Client.on_message(filters.group)
def check_message(client, message: Message):
    chat_id = message.chat.id
    user_id = None  # Initialize user_id as None

    # Check if the message has a valid user associated with it
    if message.from_user:
        user_id = message.from_user.id

    text = message.text.lower()
    
    # Check if the feature is enabled for the chat
    if chat_id in chat_settings and chat_settings[chat_id] == "on":
        # Check for forbidden content in the message
        if any(word in text for word in ["join", "bio"]) or any(link in text for link in ['https://', 'http://']):
            message.delete()
            message.reply("Please don't send messages like this.")
            
            # Send log message to the specified log channel
            if user_id:
                log_message = f"{message.from_user.first_name} ({user_id}) sent a message with forbidden content."
                client.send_message(LOG_CHANNEL, log_message)
