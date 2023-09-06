import os
import aiohttp
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from pyrogram.handlers import MessageHandler
from pyshorteners import Shortener

BITLY_API = os.environ.get("BITLY_API", "8df1df8c23f719e5cf97788cc2d40321ea30092b")
CUTTLY_API = os.environ.get("CUTTLY_API", "f64dffbde033b6c307387dd50b7c76e505f1c")
SHORTCM_API = os.environ.get("SHORTCM_API", "pk_...NIZv")
GPLINKS_API = os.environ.get("GPLINKS_API", "008ccaedd6061ad1948838f410947603de9007a7")

selected_shorteners = []

@Client.on_message(filters.command(["short"]) & filters.regex(r'https?://[^\s]+'))
async def reply_shortens(bot, update):
    reply_markup = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("Bit.ly", callback_data='shorten_bitly'),
            InlineKeyboardButton("Clck.ru", callback_data='shorten_clckru')
        ],
        [
            InlineKeyboardButton("Cutt.ly", callback_data='shorten_cuttle'),
            InlineKeyboardButton("Da.gd", callback_data='shorten_dagd')
        ],
        [
            InlineKeyboardButton("Is.gd", callback_data='shorten_isgd'),
            InlineKeyboardButton("Osdb.link", callback_data='shorten_osdb')
        ],
        [
            InlineKeyboardButton("TinyURL.com", callback_data='shorten_tinyurl'),
            InlineKeyboardButton("GPLinks.in", callback_data='shorten_gplinks')
        ],
        [   
            InlineKeyboardButton("Generate", callback_data='generate_links'),
            InlineKeyboardButton("𝘊𝘭𝘰𝘴𝘦", callback_data='close_data')
        ]
    ]
)
    message = await update.reply_text(
        text="Choose link shorteners (✔️ to select):",
        reply_markup=reply_markup,
        disable_web_page_preview=True,
        quote=True
    )

@Client.on_callback_query(filters.regex(r'shorten_'))
async def callback_shorten_links(bot, update):
    shortener = update.data.replace("shorten_", "")
    
    if shortener in selected_shorteners:
        selected_shorteners.remove(shortener)
    else:
        selected_shorteners.append(shortener)
    
    reply_markup = await create_shorteners_keyboard()
    await update.edit_message_reply_markup(reply_markup=reply_markup)

@Client.on_callback_query(filters.regex(r'generate_links'))
async def callback_generate_links(bot, update):
    link = update.message.reply_to_message.text
    shorten_urls = await short(link, selected_shorteners)
    
    await update.answer()
    await bot.send_message(
        chat_id=update.message.chat.id,
        text=shorten_urls,
        disable_web_page_preview=True
    )

@Client.on_inline_query(filters.regex(r'https?://[^\s]+'))
async def inline_short(bot, update):
    link = update.matches[0].group(0)
    answers = []
    
    for service in ["bitly", "clckru", "cuttle", "dagd", "isgd", "osdb", "tinyurl", "gplinks"]:
        shorten_url = await short(link, service)
        answers.append(
            InlineQueryResultArticle(
                title=f"{service.capitalize()} Short Link",
                description=update.query,
                input_message_content=InputTextMessageContent(
                    message_text=shorten_url,
                    disable_web_page_preview=True
                )
            )
        )
    
    await bot.answer_inline_query(
        inline_query_id=update.id,
        results=answers
    )

async def short(link, services):
    try:
        shorten_urls = "**--Shortened URLs--**\n"
        
        for service in services:
            # Bit.ly shorten
            if service == "bitly" and BITLY_API:
                s = Shortener(api_key=BITLY_API)
                url = s.bitly.short(link)
                shorten_urls += f"\n**Bit.ly :-** {url}"
            
            # Clck.ru shorten
            elif service == "clckru":
                s = Shortener()
                url = s.clckru.short(link)
                shorten_urls += f"\n**Clck.ru :-** {url}"
            
            # Cutt.ly shorten
            elif service == "cuttle" and CUTTLY_API:
                s = Shortener(api_key=CUTTLY_API)
                url = s.cuttly.short(link)
                shorten_urls += f"\n**Cutt.ly :-** {url}"
            
            # Da.gd shorten
            elif service == "dagd":
                s = Shortener()
                url = s.dagd.short(link)
                shorten_urls += f"\n**Da.gd :-** {url}"
            
            # Is.gd shorten
            elif service == "isgd":
                s = Shortener()
                url = s.isgd.short(link)
                shorten_urls += f"\n**Is.gd :-** {url}"
            
            # Osdb.link shorten
            elif service == "osdb":
                s = Shortener()
                url = s.osdb.short(link)
                shorten_urls += f"\n**Osdb.link :-** {url}"
            
            # TinyURL.com shorten
            elif service == "tinyurl":
                s = Shortener()
                url = s.tinyurl.short(link)
                shorten_urls += f"\n**TinyURL.com :-** {url}"
            
            # GPLinks shorten
            elif service == "gplinks":
                api_url = "https://gplinks.in/api"
                params = {'api': GPLINKS_API, 'url': link}
                async with aiohttp.ClientSession() as session:
                    async with session.get(api_url, params=params, raise_for_status=True) as response:
                        data = await response.json()
                        url = data["shortenedUrl"]
                        shorten_urls += f"\n**GPLinks.in :-** {url}"
        
        return shorten_urls
    except Exception as error:
        return f"Error: {error}"

async def create_shorteners_keyboard():
    buttons = []
    for service in ["bitly", "clckru", "cuttle", "dagd", "isgd", "osdb", "tinyurl", "gplinks"]:
        button_text = f"{service.capitalize()} ✔️" if service in selected_shorteners else f"{service.capitalize()}"
        buttons.append(
            InlineKeyboardButton(button_text, callback_data=f'shorten_{service}')
        )
    
    buttons.append(InlineKeyboardButton("Generate", callback_data='generate_links'))
    buttons.append(InlineKeyboardButton("𝘊𝘭𝘰𝘴𝘦", callback_data='close_data'))
    
    return InlineKeyboardMarkup([buttons])
    
