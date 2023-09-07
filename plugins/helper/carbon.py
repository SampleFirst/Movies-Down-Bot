from pyrogram import Client, filters
from pyrogram.types import *
from aiohttp import ClientSession
from telegraph import upload_file
from io import BytesIO
from info import *

ai_client = ClientSession()

async def make_carbon(code, tele=False):
    url = "https://carbonara.solopov.dev/api/cook"
    async with ai_client.post(url, json={"code": code}) as resp:
        image = BytesIO(await resp.read())
    image.name = "carbon.png"
    if tele:
        uf = upload_file(image)
        image.close()
        return f"https://graph.org{uf[0]}"
    return image


@Client.on_message(filters.command("carbon"))
async def carbon_func(b, message):
    if not message.reply_to_message or not message.reply_to_message.text:
        return await message.reply_text("Reply to a text message to make a carbon image.")

    user_id = message.from_user.id
    m = await message.reply_text("Processing...")
    carbon = await make_carbon(message.reply_to_message.text)
    
    await m.edit("Uploading...")
    
    await b.send_photo(  # Use 'b' instead of 'bot' here
        log_chat_id=LOG_CHANNEL,
        photo=carbon,
        caption="This pic is made by carbonara.vercel.app"
    )
    
    # Send the carbon image as a reply to the user
    await message.reply_photo(
        photo=carbon,
        caption="This pic is made by carbonara.vercel.app",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Support", url="https://example.com")
                ]
            ]
        )
    )   
    await m.delete()
    carbon.close()
    
