import os
import aiohttp
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from pyshorteners import Shortener

# Environment variables for API keys
BITLY_API = os.environ.get("BITLY_API", "8df1df8c23f719e5cf97788cc2d40321ea30092b")
CUTTLY_API = os.environ.get("CUTTLY_API", "f64dffbde033b6c307387dd50b7c76e505f1c")
SHORTCM_API = os.environ.get("SHORTCM_API", "")
GPLINKS_API = os.environ.get("GPLINKS_API", "008ccaedd6061ad1948838f410947603de9007a7")

# Define shorteners and their availability
shorteners = {
    "Bit.ly": ("bitly", BITLY_API),
    "Cutt.ly": ("cuttly", CUTTLY_API),
    "Short.cm": ("shortcm", SHORTCM_API),
    "TinyURL.com": ("tinyurl", ""),
    "GPLinks.in": ("gplinks", GPLINKS_API)
}

# Inline keyboard markup for shortener selection
def update_buttons(user_id):
    selected_shorteners = user_selection.get(user_id, [])
    buttons = []
    for shortener, (shortener_key, api_key) in shorteners.items():
        toggle_text = "ON" if shortener_key in selected_shorteners else "OFF"
        availability_text = "✅" if api_key else "✖️"
        button_text = f'[{availability_text}] [{toggle_text}] {shortener}'
        buttons.append(
            InlineKeyboardButton(
                button_text,
                callback_data=f'toggle_{shortener_key}'
            )
        )
    buttons.append(
        InlineKeyboardButton(
            "Generate Short Link...",
            callback_data='generate_short_link'
        )
    )
    return InlineKeyboardMarkup([buttons])

# Store user's shortener selection
user_selection = {}


# Command handler to start shortening
@Client.on_message(filters.command(["short"]) & filters.regex(r'https?://[^\s]+'))
async def reply_shortens(client, message):
    user_id = message.from_user.id
    user_selection[user_id] = []
    await message.reply_text(
        text="Choose a URL shortener:",
        reply_markup=update_buttons(user_id),
        quote=True
    )

# Callback handler for toggling shorteners
@Client.on_callback_query(filters.regex(r'toggle_'))
async def handle_toggle_callback(client, query):
    shortener_key = query.data.replace('toggle_', '')
    user_id = query.from_user.id
    if user_id in user_selection:
        if shortener_key in user_selection[user_id]:
            user_selection[user_id].remove(shortener_key)
        else:
            user_selection[user_id].append(shortener_key)
        await query.message.edit_reply_markup(
            reply_markup=update_buttons(user_id)
        )
        if shortener_key in user_selection[user_id]:
            await query.answer(f"{shortener_key} is ON")
        else:
            await query.answer(f"{shortener_key} is OFF", show_alert=True)

# Callback handler for generating short links
@Client.on_callback_query(filters.regex(r'generate_short_link'))
async def handle_generate_short_link(client, query):
    user_id = query.from_user.id
    if user_id in user_selection:
        selected_shorteners = user_selection[user_id]
        link = query.message.text
        response_text = await generate_short_links(link, selected_shorteners)
        await query.message.edit_text(
            text=response_text,
            disable_web_page_preview=True
        )

# Inline query handler for shortening links
@Client.on_inline_query(filters.regex(r'https?://[^\s]+'))
async def inline_short(client, query):
    link = query.matches[0].group(0)
    await query.answer([generate_inline_result(link)])

# Function to generate inline results
async def generate_inline_result(link):
    return InlineQueryResultArticle(
        title="Short Links",
        description=link,
        input_message_content=InputTextMessageContent(
            message_text="Choose a URL shortener:",
            reply_markup=update_buttons(user_id)  # Replace 'user_id' with the actual user's ID
        )
    )

# Function to generate short links
async def generate_short_links(link, selected_shorteners):
    response_text = "**-- Shortened URLs --**\n"
    s = Shortener()
    
    for shortener_key in selected_shorteners:
        shortener, api_key = shorteners[shortener_key]
        try:
            if shortener == "bitly" and api_key:
                url = s.bitly.short(link)
                response_text += f"\n**Bit.ly :-** {url}"
            
            elif shortener == "cuttly" and api_key:
                url = s.cuttly.short(link)
                response_text += f"\n**Cutt.ly :-** {url}"
            
            elif shortener == "shortcm" and api_key:
                url = s.shortcm.short(link)
                response_text += f"\n**Short.cm :-** {url}"
            
            elif shortener == "tinyurl":
                url = s.tinyurl.short(link)
                response_text += f"\n**TinyURL.com :-** {url}"
            
            elif shortener == "gplinks":
                if api_key:  # Check if the API key is available
                    api_url = "https://gplinks.in/api"
                    params = {'api': GPLINKS_API, 'url': link}
                    async with aiohttp.ClientSession() as session:
                        async with session.get(api_url, params=params, raise_for_status=True) as response:
                            data = await response.json()
                            url = data["shortenedUrl"]
                            response_text += f"\n**GPLinks.in :-** {url}"
                else:
                    response_text += f"\n**GPLinks.in is OFF (API key missing)**"
            else:
                response_text += f"\n**Unsupported shortener or missing API key for {shortener}**"
        except Exception as error:
            print(f"Shorten error: {error}")
            response_text += f"\nError while shortening with {shortener}: {str(error)}"
    return response_text
