import pyrogram
from pyrogram import filters
from pyrogram import Client
from pyrogram.types import Message
import re
from info import ADMINS 

# Define the allowed terms
ALLOW_LINKS = ["https://t.me/iPapkornMoviesGroup"]
ALLOW_MENTION = ["admin"]  # Remove the "@" symbol
BANNED_WORDS = ["join", "bio"]

# Initialize counters for warnings
links_warnings = {}
mention_warnings = {}
word_warnings = {}

# Define a function to check for links in messages
def check_links(client, message):
    text = message.text.lower()
    for link in ALLOW_LINKS:
        if link in text:
            return True 
    return False 

# Define a function to check for usernames in messages
def check_usernames(client, message):
    text = message.text.lower()
    for username in ALLOW_MENTION:
        if username in text:
            return True 
    return False 

# Define a function to check for banned words in messages
def check_banned_words(client, message):
    text = message.text.lower()
    for word in BANNED_WORDS:
        if word in text:
            return False 
    return True 
    
@Client.on_message(filters.text & filters.group)
async def delete_and_warn(client, message: Message):
    user_id = message.from_user.id
    
    # Skip checking warnings for users in ADMINS
    if user_id in ADMINS:
        return
    
    if check_links(client, message):
        if user_id not in links_warnings:
            links_warnings[user_id] = 0
        links_warnings[user_id] += 1
        client.send_message(message.chat.id, f"Warning: Please do not send links ({links_warnings[user_id]}/3)")
        if links_warnings[user_id] >= 3:
            client.kick_chat_member(message.chat.id, user_id)
            del links_warnings[user_id]
        return True

    if check_usernames(client, message):
        if user_id not in mention_warnings:
            mention_warnings[user_id] = 0
        mention_warnings[user_id] += 1
        client.send_message(message.chat.id, f"Warning: Please do not mention usernames ({mention_warnings[user_id]}/3)")
        if mention_warnings[user_id] >= 3:
            client.kick_chat_member(message.chat.id, user_id)
            del mention_warnings[user_id]
        return True

    if check_banned_words(client, message):
        if user_id not in word_warnings:
            word_warnings[user_id] = 0
        word_warnings[user_id] += 1
        client.send_message(message.chat.id, f"Warning: Please do not use banned words ({word_warnings[user_id]}/3)")
        if word_warnings[user_id] >= 3:
            client.kick_chat_member(message.chat.id, user_id)
            del word_warnings[user_id]
        return True
