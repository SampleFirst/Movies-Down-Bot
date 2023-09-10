import time
from pyrogram import Client, filters

# Constants
ALIVE = "<b>I'm alive and kicking! You're still here, right? Seems like you don't have any affection towards me. It's fine... You can try /start to see if something changes...🙂</b>"


# Command handlers
@Client.on_message(filters.command("alive"))
async def check_alive(_, message):
    await message.reply_text(ALIVE)

@Client.on_message(filters.command("ping"))
async def ping(_, message):
    start_time = time.time()
    text = await message.reply_text("Pinging...")
    end_time = time.time()
    time_taken_ms = (end_time - start_time) * 1000
    await text.edit(f"<b>Pong!\n{time_taken_ms:.3f} ms</b>")
