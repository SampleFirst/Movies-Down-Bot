from countryinfo import CountryInfo
from pyrogram import filters, Client 
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

@Client.on_message(filters.command(["country"]))
async def country_info(bot, message):
    # Get the text after the /country command
    input_text = message.text.split(" ", 1)[1]
    
    try:
        country = CountryInfo(input_text)
    except Exception as error:
        await message.reply_text(
            text=f"Error: {error}",
            quote=True
        )
        return

    info = f"""𝖢𝗈𝗎𝗇𝗍𝗋𝗒 𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝗍𝗂𝗈𝗇
𝖭𝖺𝗆𝖾 : {country.name()}
𝖭𝖺𝗍𝗂𝗏𝖾 𝖭𝖺𝗆𝖾 : {country.native_name()}
𝖢𝖺𝗉𝗂𝗍𝖺𝗅 : {country.capital()}
Population : <code>{country.population()}</code>
𝖱𝖾𝗀𝗂𝗈𝗇 : {country.region()}
𝖲𝗎𝖻 𝖱𝖾𝗀𝗂𝗈𝗇 : {country.subregion()}
𝖳𝗈𝗉 𝖫𝖾𝗏𝖾𝗅 𝖣𝗈𝗆𝖺𝗂𝗇𝗌 : {country.tld()}
𝖢𝖺𝗅𝗅𝗂𝗇𝗀 𝖢𝗈𝖽𝖾𝗌 : {country.calling_codes()}
𝖢𝗎𝗋𝗋𝖾𝗇𝖼𝗂𝖾𝗌 : {country.currencies()}
𝖱𝖾𝗌𝗂𝖽𝖾𝗇𝖼𝖾 : {country.demonym()}
𝖳𝗂𝗆𝖾𝗓𝗈𝗇𝖾 : <code>{country.timezones()}</code>
"""

    country_name = country.name().replace(" ", "+")
    
    buttons = [
        [
            InlineKeyboardButton("ᴡɪᴋɪᴘᴇᴅɪᴀ", url=f"{country.wiki()}"),
            InlineKeyboardButton("ɢᴏᴏɢʟᴇ", url=f"https://www.google.com/search?q={country_name}")
        ],
        [
            InlineKeyboardButton('ᴄʟᴏsᴇ', callback_data='close_data')
        ]
    ]
    
    try:
        await message.reply_photo(
            photo="https://telegra.ph/file/834750cfadc32b359b40c.jpg",
            caption=info,
            reply_markup=InlineKeyboardMarkup(buttons),
            quote=True
        )
    except Exception as error:
        await message.reply_text(
            text=f"Error: {error}",
            quote=True
        )
