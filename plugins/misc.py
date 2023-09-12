# Standard Library Imports
import os
import logging
import time
from datetime import datetime

# Pyrogram Library Imports
from pyrogram import Client, filters, enums
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant, MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# Local Imports
from info import IMDB_TEMPLATE
from utils import extract_user, get_file_id, get_poster, last_online

# Logging Configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


@Client.on_message(filters.command('id'))
async def show_id_info(client, message):
    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        user = message.from_user
        user_id = user.id
        first_name = user.first_name
        last_name = user.last_name or ""
        username = user.username
        dc_id = user.dc_id or ""
        
        response_text = (
            f"<b>➲ First Name:</b> {first_name}\n"
            f"<b>➲ Last Name:</b> {last_name}\n"
            f"<b>➲ Username:</b> {username}\n"
            f"<b>➲ Telegram ID:</b> <code>{user_id}</code>\n"
            f"<b>➲ Data Centre:</b> <code>{dc_id}</code>"
        )

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        chat_id = message.chat.id
        user_id = message.from_user.id if message.from_user else 'Anonymous'
        reply_user_id = (
            message.reply_to_message.from_user.id 
            if message.reply_to_message and message.reply_to_message.from_user
            else 'Anonymous'
        )
        
        file_info = get_file_id(message.reply_to_message) if message.reply_to_message else get_file_id(message)

        response_text = (
            f"<b>➲ Chat ID:</b> <code>{chat_id}</code>\n"
            f"<b>➲ User ID:</b> <code>{user_id}</code>\n"
            f"<b>➲ Replied User ID:</b> <code>{reply_user_id}</code>\n"
        )

        if file_info:
            response_text += (
                f"<b>{file_info.message_type}:</b> "
                f"<code>{file_info.file_id}</code>\n"
            )

    await message.reply_text(response_text, quote=True)

@Client.on_message(filters.command(["info"]))
async def who_is(client, message):
    status_message = await message.reply_text(
        "`Fetching user info...`"
    )
    
    await status_message.edit(
        "`Processing user info...`"
    )

    from_user = None
    from_user_id, _ = extract_user(message)

    try:
        from_user = await client.get_users(from_user_id)
    except Exception as error:
        await status_message.edit(str(error))
        return

    if from_user is None:
        return await status_message.edit("No valid user_id / message specified")

    message_out_str = ""
    message_out_str += f"<b>➲ First Name:</b> {from_user.first_name}\n"
    last_name = from_user.last_name or "<b>None</b>"
    message_out_str += f"<b>➲ Last Name:</b> {last_name}\n"
    message_out_str += f"<b>➲ Telegram ID:</b> <code>{from_user.id}</code>\n"
    username = from_user.username or "<b>None</b>"
    dc_id = from_user.dc_id or "[User Doesn't Have A Valid DP]"
    message_out_str += f"<b>➲ Data Centre:</b> <code>{dc_id}</code>\n"
    message_out_str += f"<b>➲ User Name:</b> @{username}\n"
    message_out_str += f"<b>➲ User Link:</b> <a href='tg://user?id={from_user.id}'><b>Click Here</b></a>\n"

    if message.chat.type in ["supergroup", "channel"]:
        try:
            chat_member = await message.chat.get_member(from_user.id)
            joined_date = (
                chat_member.joined_date or datetime.now()
            ).strftime("%Y.%m.%d %H:%M:%S")
            message_out_str += (
                "<b>➲ Joined this Chat on:</b> <code>"
                f"{joined_date}"
                "</code>\n"
            )
        except UserNotParticipant:
            pass

    chat_photo = from_user.photo

    if chat_photo:
        local_user_photo = await client.download_media(
            message=chat_photo.big_file_id
        )

        buttons = [[
            InlineKeyboardButton('🔐 Close', callback_data='close_data')
        ]]

        reply_markup = InlineKeyboardMarkup(buttons)

        await message.reply_photo(
            photo=local_user_photo,
            quote=True,
            reply_markup=reply_markup,
            caption=message_out_str,
            parse_mode="html",
            disable_notification=True
        )

        os.remove(local_user_photo)
    else:
        buttons = [[
            InlineKeyboardButton('🔐 Close', callback_data='close_data')
        ]]

        reply_markup = InlineKeyboardMarkup(buttons)

        await message.reply_text(
            text=message_out_str,
            reply_markup=reply_markup,
            quote=True,
            parse_mode="html",
            disable_notification=True
        )

    await status_message.delete()

@Client.on_message(filters.command(["imdb", 'search']))
async def imdb_search(client, message):
    if ' ' in message.text:
        k = await message.reply('Searching IMDb')
        r, title = message.text.split(None, 1)
        movies = await get_poster(title, bulk=True)
        if not movies:
            return await message.reply("No results found")
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{movie.get('title')} - {movie.get('year')}",
                    callback_data=f"imdb#{movie.movieID}",
                )
            ]
            for movie in movies
        ]
        await k.edit('Here is what I found on IMDb', reply_markup=InlineKeyboardMarkup(btn))
    else:
        await message.reply('Give me a movie / series name')

@Client.on_callback_query(filters.regex('^imdb'))
async def imdb_callback(bot: Client, query: CallbackQuery):
    i, movie = query.data.split('#')
    imdb = await get_poster(query=movie, id=True)
    btn = [
        [
            InlineKeyboardButton(
                text=f"{imdb.get('title')}",
                url=imdb['url'],
            )
        ]
    ]
    message = query.message.reply_to_message or query.message
    if imdb:
        caption = IMDB_TEMPLATE.format(
            query = imdb['title'],
            title = imdb['title'],
            votes = imdb['votes'],
            aka = imdb["aka"],
            seasons = imdb["seasons"],
            box_office = imdb['box_office'],
            localized_title = imdb['localized_title'],
            kind = imdb['kind'],
            imdb_id = imdb["imdb_id"],
            cast = imdb["cast"],
            runtime = imdb["runtime"],
            countries = imdb["countries"],
            certificates = imdb["certificates"],
            languages = imdb["languages"],
            director = imdb["director"],
            writer = imdb["writer"],
            producer = imdb["producer"],
            composer = imdb["composer"],
            cinematographer = imdb["cinematographer"],
            music_team = imdb["music_team"],
            distributors = imdb["distributors"],
            release_date = imdb['release_date'],
            year = imdb['year'],
            genres = imdb['genres'],
            poster = imdb['poster'],
            plot = imdb['plot'],
            rating = imdb['rating'],
            url = imdb['url'],
            **locals()
        )
    else:
        caption = "No Results"
    if imdb.get('poster'):
        try:
            await query.message.reply_photo(photo=imdb['poster'], caption=caption, reply_markup=InlineKeyboardMarkup(btn))
        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
            pic = imdb.get('poster')
            poster = pic.replace('.jpg', "._V1_UX360.jpg")
            await query.message.reply_photo(photo=poster, caption=caption, reply_markup=InlineKeyboardMarkup(btn))
        except Exception as e:
            logging.exception(e)
            await query.message.reply(caption, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=False)
        await query.message.delete()
    else:
        await query.message.edit(caption, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=False)
    await query.answer()
    
