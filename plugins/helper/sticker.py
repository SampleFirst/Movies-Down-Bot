from pyrogram import Client, filters
from pyrogram.types import Update


@Client.on_message(filters.command(["stickerid"]))
async def sticker_id(bot, update: Update):
    if update.message.reply_to_message and update.message.reply_to_message.sticker:
        sticker = update.message.reply_to_message.sticker
        await update.reply(
            f"**Sticker ID is**  \n `{sticker.file_id}` \n \n **Unique ID is** \n\n`{sticker.file_unique_id}`",
            quote=True
        )
    else:
        await update.reply("Please reply to a sticker with the /stickerid command.")
