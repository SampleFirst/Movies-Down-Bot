import os
from pyrogram import filters
from aiohttp import ClientSession
from pyrogram import Client as bot
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from io import BytesIO
import aiofiles
from PIL import Image
from info import S_GROUP, LOG_CHANNEL

# Initialize an aiohttp client session
aiohttpsession = ClientSession()


# Function to create a carbon image from text
async def make_carbon(code):
    url = "https://carbonara.vercel.app/api/cook"
    async with aiohttpsession.post(url, json={"code": code}) as resp:
        image = BytesIO(await resp.read())
    image.name = "carbon.png"
    return image

# Define a command handler for /carbon
@bot.on_message(filters.command("carbon"))
async def carbon_func(client, message):
    if not message.reply_to_message or not message.reply_to_message.text:
        return await message.reply_text("Please reply to a text message to make a carbon image.")
    
    # Inform the user that the process is ongoing
    m = await message.reply_text("Processing...")

    try:
        # Create a carbon image from the replied text
        carbon = await make_carbon(message.reply_to_message.text)

        if carbon:
            # Inform the user that the image is being uploaded
            await m.edit("Uploading...")

            # Reply with the carbon image and a support button
            await client.send_photo(
                chat_id=message.chat.id,
                photo=carbon,
                caption="**This pic is a nice one...**",
                reply_markup=InlineKeyboardMarkup(
                    [
                        InlineKeyboardButton("Support", url=S_GROUP)
                    ]
                ),
            )

            # Send the same photo to the LOG_CHANNEL with a message
            await client.send_photo(
                chat_id=LOG_CHANNEL,
                photo=carbon,
                caption=f"**User @{message.from_user.username} generated a carbon image**"
            )

            # Delete the processing message and close the image
            await m.delete()
            carbon.close()
        else:
            await m.edit("Failed to generate a valid image.")
    except Exception as e:
        await m.edit(f"An error occurred: {str(e)}")
        
