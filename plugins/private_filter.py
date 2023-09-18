# Standard imports
import asyncio
import logging
import re
import ast
import math

# Third Party imports 
from pyrogram import Client, filters, enums
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# Database Imports
from database.users_chats_db import db
from database.ia_filterdb import Media, get_file_details, get_search_results
from database.filters_mdb import (
    del_all,
    find_filter,
    get_filters,
)
from database.gfilters_mdb import (
    find_gfilter,
    get_gfilters,
)
from plugins.pm_filter import global_filters

# Local Imports
from Script import script
from utils import (
    get_shortlink,
    get_size,
    is_subscribed,
    get_poster,
    search_gagala,
    temp,
    get_settings,
    save_group_settings,
)
from info import *
    

# Set the logging level to ERROR
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

BUTTONS = {}
SPELL_CHECK = {}
FILTER_MODE = {}

@Client.on_message(filters.private & filters.text)
async def auto_pm_fill(b, m):
    if PMFILTER:       
        if G_FILTER:
            kd = await global_filters(b, m)
            if kd == False: await pm_auto_filter(b, m)
        else: await pm_auto_filter(b, m)
    else: return 
        
@Client.on_message(filters.private & filters.text & filters.incoming)
async def pm_text(bot, message):
    await global_filters(bot, message)
    user_id = message.chat.id
    name = message.text

    keywords = await get_filters(user_id)
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_filter(user_id, keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            await message.reply_text(reply_text, disable_web_page_preview=True)
                        else:
                            button = eval(btn)
                            await message.reply_text(
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button)
                            )
                    elif btn == "[]":
                        await message.reply_cached_media(
                            fileid,
                            caption=reply_text or ""
                        )
                    else:
                        button = eval(btn)
                        await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button)
                        )
                except Exception as e:
                    print(e)
                break

    else:
        if FILTER_MODE.get(str(user_id)) == "False":
            return
        else:
            await pm_auto_filter(bot, message)
            
            

@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    try:
        offset = int(offset)
    except:
        offset = 0
    search = BUTTONS.get(key)
    if not search:
        await query.answer("No more results found.", show_alert=True)
        return

    files, n_offset, total = await get_search_results(search, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return

    # Handle shortlinks or buttons based on your preferences
    # Replace this section with your desired logic

    if 0 < offset <= 10:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 10
    if n_offset == 0:
        btn = [
            [InlineKeyboardButton("⌫ Back", callback_data=f"next_{req}_{key}_{off_set}"),
             InlineKeyboardButton(f"Page {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}",
                                  callback_data="pages")]
        ]
    elif off_set is None:
        btn = [
            [InlineKeyboardButton(f"Page {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
             InlineKeyboardButton("Next ⌦", callback_data=f"next_{req}_{key}_{n_offset}")]
        ]
    else:
        btn = [
            [
                InlineKeyboardButton("⌫ Back", callback_data=f"next_{req}_{key}_{off_set}"),
                InlineKeyboardButton(f"Page {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
                InlineKeyboardButton("Next ⌦", callback_data=f"next_{req}_{key}_{n_offset}")
            ],
        ]
    try:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass
    await query.answer()
    
    
@Client.on_callback_query(filters.regex(r"^spol"))
async def advantage_pm_spoll_choker(bot, query):
    _, user, movie_ = query.data.split('#')
    movies = SPELL_CHECK.get(query.message.reply_to_message.id)
    if not movies:
        return await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    if movie_ == "close_spellcheck":
        return await query.message.delete()
    movie = movies[(int(movie_))]
    await query.answer(script.TOP_ALRT_MSG)
    
    # Replace group filters with private filters
    k = await private_manual_filters(bot, query.message, text=movie)
    
    if k == False:
        files, offset, total_results = await get_search_results(movie, offset=0, filter=True)
        if files:
            k = (movie, files, offset, total_results)
            await pm_auto_filter(bot, query, k)
        else:
            reqstr1 = query.from_user.id if query.from_user else 0
            reqstr = await bot.get_users(reqstr1)
            await bot.send_message(chat_id=LOG_CHANNEL, text=(script.NORSLTS.format(reqstr.id, reqstr.mention, movie)))
            k = await query.message.edit(script.MVE_NT_FND)
            await asyncio.sleep(10)
            await k.delete()


async def pm_auto_filter(bot, msg):
    reqstr1 = msg.from_user.id if msg.from_user else 0
    reqstr = await bot.get_users(reqstr1)
    
    message = msg
    settings = await get_private_settings(message.from_user.id)  # Update to get private settings
    
    if message.text.startswith("/"):
        return  # Ignore commands

    if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
        return

    if len(message.text) < 100:
        search = message.text
        files, offset, total_results = await get_search_results(search.lower(), offset=0, filter=True)
        
        if not files:
            if settings["spell_check"]:
                return await advantage_spell_chok(bot, msg)
            else:
                await bot.send_message(chat_id=LOG_CHANNEL, text=(script.NORSLTS.format(reqstr.id, reqstr.mention, search)))
                return
    else:
        return

    if 'is_shortlink' in settings.keys():
        ENABLE_SHORTLINK = settings['is_shortlink']
    else:
        await save_private_settings(message.from_user.id, 'is_shortlink', False)
        ENABLE_SHORTLINK = False
    
    pre = 'filep' if settings['file_secure'] else 'file'

    if ENABLE_SHORTLINK == True:
        # Update URL creation to use private settings
        btn = [
            [
                InlineKeyboardButton(
                    text=f"[{get_size(file.file_size)}] {file.file_name}",
                    url=await get_shortlink_private(message.from_user.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                ),
            ]
            for file in files
        ]
    else:
        # Update callback data creation to use private settings
        btn = [
            [
                InlineKeyboardButton(
                    text=f"[{get_size(file.file_size)}] {file.file_name}",
                    callback_data=f'{pre}#{file.file_id}'
                ),
            ]
            for file in files
        ]

    imdb = await get_poster(search, file=(files[0]).file_name) if settings["imdb"] else None
    TEMPLATE = settings['template']

    if imdb:
        # Update the caption to use private settings
        cap = TEMPLATE.format(
            query=search,
            title=imdb['title'],
            votes=imdb['votes'],
            aka=imdb["aka"],
            seasons=imdb["seasons"],
            box_office=imdb['box_office'],
            localized_title=imdb['localized_title'],
            kind=imdb['kind'],
            imdb_id=imdb["imdb_id"],
            cast=imdb["cast"],
            runtime=imdb["runtime"],
            countries=imdb["countries"],
            certificates=imdb["certificates"],
            languages=imdb["languages"],
            director=imdb["director"],
            writer=imdb["writer"],
            producer=imdb["producer"],
            composer=imdb["composer"],
            cinematographer=imdb["cinematographer"],
            music_team=imdb["music_team"],
            distributors=imdb["distributors"],
            release_date=imdb['release_date'],
            year=imdb['year'],
            genres=imdb['genres'],
            poster=imdb['poster'],
            plot=imdb['plot'],
            rating=imdb['rating'],
            url=imdb['url'],
            **locals()
        )
    else:
        cap = f"<b><i>𝙃𝙚𝙧𝙚 𝙞𝙨 𝙬𝙝𝙖𝙩 𝙞𝙨 𝙛𝙤𝙪𝙣𝙙 𝙮𝙤𝙪𝙧 𝙦𝙪𝙚𝙧𝙮:\n {search}\n👤𝙍𝙚𝙦𝙪𝙚𝙨𝙩𝙚𝙙 𝘽𝙮 : {message.from_user.mention}\n</i></b>"
    
    if imdb and imdb.get('poster'):
        try:
            hehe = await message.reply_photo(photo=imdb.get('poster'), caption=cap[:1024], reply_markup=InlineKeyboardMarkup(btn))
            if settings['auto_delete']:
                await asyncio.sleep(600)
                await hehe.delete()
                await message.delete()
        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
            pic = imdb.get('poster')
            poster = pic.replace('.jpg', "._V1_UX360.jpg")
            hmm = await message.reply_photo(photo=poster, caption=cap[:1024], reply_markup=InlineKeyboardMarkup(btn))
            if settings['auto_delete']:
                await asyncio.sleep(600)
                await hmm.delete()
                await message.delete()
        except Exception as e:
            logger.exception(e)
            fek = await message.reply_photo(photo=NOR_IMG, caption=cap, reply_markup=InlineKeyboardMarkup(btn))
            if settings['auto_delete']:
                await asyncio.sleep(600)
                await fek.delete()
                await message.delete()
    else:
        fuk = await message.reply_photo(photo=NOR_IMG, caption=cap, reply_markup=InlineKeyboardMarkup(btn))
        if settings['auto_delete']:
            await asyncio.sleep(600)
            await fuk.delete()
            await message.delete()






@Client.on_message(filters.private & filters.command("spellcheck"))
async def advantage_pm_spell_chok(bot, msg):
    mv_id = msg.message_id
    mv_rqst = msg.text
    reqstr1 = msg.from_user.id
    reqstr = await bot.get_users(reqstr1)
    
    settings = await get_settings(msg.chat.id)
    query = re.sub(
        r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)",
        "", mv_rqst, flags=re.IGNORECASE)  # plis contribute some common words
    
    RQST = query.strip()
    query = query.strip() + " movie"
    
    try:
        movies = await get_poster(mv_rqst, bulk=True)
    except Exception as e:
        logger.exception(e)
        await bot.send_message(chat_id=LOG_CHANNEL, text=(script.NORSLTS.format(reqstr.id, reqstr.mention, mv_rqst)))
        k = await msg.reply(script.I_CUDNT.format(reqstr.mention))
        await asyncio.sleep(8)
        await k.delete()
        return
    
    movielist = []
    
    if not movies:
        reqst_gle = mv_rqst.replace(" ", "+")
        button = [[
            InlineKeyboardButton("Google", url=f"https://www.google.com/search?q={reqst_gle}")
        ]]
        await bot.send_message(chat_id=LOG_CHANNEL, text=(script.NORSLTS.format(reqstr.id, reqstr.mention, mv_rqst)))
        k = await msg.reply_photo(
            photo=SPELL_IMG,
            caption=script.I_CUDNT.format(mv_rqst),
            reply_markup=InlineKeyboardMarkup(button)
        )
        await asyncio.sleep(30)
        await k.delete()
        return
    
    movielist += [movie.get('title') for movie in movies]
    movielist += [f"{movie.get('title')} {movie.get('year')}" for movie in movies]
    SPELL_CHECK[mv_id] = movielist
    
    btn = [
        [
            InlineKeyboardButton(
                text=movie_name.strip(),
                callback_data=f"spol#{reqstr1}#{k}",
            )
        ]
        for k, movie_name in enumerate(movielist)
    ]
    
    btn.append([InlineKeyboardButton(text="Close", callback_data=f'spol#{reqstr1}#close_spellcheck')])
    spell_check_del = await msg.reply_photo(
        photo=(SPELL_IMG),
        caption=(script.CUDNT_FND.format(reqstr.mention)),
        reply_markup=InlineKeyboardMarkup(btn)
    )

    try:
        if settings['auto_delete']:
            await asyncio.sleep(600)
            await spell_check_del.delete()
    except KeyError:
        grpid = await active_connection(str(msg.from_user.id))
        await save_group_settings(grpid, 'auto_delete', True)
        settings = await get_settings(msg.chat.id)
        if settings['auto_delete']:
            await asyncio.sleep(600)
            await spell_check_del.delete()


