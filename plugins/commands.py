# Standard Library Imports
import os
import re
import json
import base64
import logging
import random
import asyncio

# Pyrogram Library Imports
from pyrogram import Client, filters
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Database Imports
from database.ia_filterdb import Media, get_file_details, unpack_new_file_id
from database.users_chats_db import db
from database.connections_mdb import active_connection

# Local Imports
from Script import script
from utils import get_settings, get_size, is_subscribed, save_group_settings, temp

# Environment Variables
from info import(
    CHANNELS, 
    ADMINS, 
    AUTH_CHANNEL, 
    LOG_CHANNEL, 
    PICS, 
    BATCH_FILE_CAPTION, 
    CUSTOM_FILE_CAPTION, 
    PROTECT_CONTENT, 
    MSG_ALRT, 
    MAIN_CHANNEL
)

# Logging Configuration
logger = logging.getLogger(__name__)

# Global Variables
BATCH_FILES = {}

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        buttons = [
            [
                InlineKeyboardButton('🤖 Updates', url=MAIN_CHANNEL)
            ],
            [
                InlineKeyboardButton('ʜᴇʟᴘ', url=f"https://t.me/{temp.U_NAME}?start=help"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply(script.START_TXT.format(message.from_user.mention if message.from_user else message.chat.title, temp.U_NAME, temp.B_NAME), reply_markup=reply_markup)
        await asyncio.sleep(2)
        if not await db.get_chat(message.chat.id):
            total = await client.get_chat_members_count(message.chat.id)
            await client.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total, "Unknown"))
            await db.add_chat(message.chat.id, message.chat.title)
        return

    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention))

    if len(message.command) != 2:
        buttons = [
            [
                InlineKeyboardButton('sᴜʀᴘʀɪsᴇ', callback_data='start')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        m = await message.reply_sticker("CAACAgUAAxkBAAINdmL9uWnC3ptj9YnTjFU4YGr5dtzwAAIEAAPBJDExieUdbguzyBAeBA")
        await asyncio.sleep(1)
        await m.delete()
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.SUR_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return
    if AUTH_CHANNEL and not await is_subscribed(client, message):
        try:
            invite_link = await client.create_chat_invite_link(int(temp.AUTH_CHANNEL))
        except ChatAdminRequired:
            logger.error("Make sure Bot is an admin in Forcesub channel")
            return
        btn = [
            [
                InlineKeyboardButton("🤖 Join Updates Channel", url=invite_link.invite_link)
            ]
        ]

        if len(message.command) == 2:
            command = message.command[1]
            if command != "subscribe":
                try:
                    kk, file_id = command.split("_", 1)
                    pre = 'checksubp' if kk == 'filep' else 'checksub'
                    btn.append([InlineKeyboardButton(" 🔄 Try Again", callback_data=f"{pre}#{file_id}")])
                except (IndexError, ValueError):
                    btn.append([InlineKeyboardButton(" 🔄 Try Again", url=f"https://t.me/{temp.U_NAME}?start={command}")])

        await client.send_message(
            chat_id=message.from_user.id,
            text="**Please Join My Updates Channel to use this Bot!**",
            reply_markup=InlineKeyboardMarkup(btn),
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return

    if len(message.command) == 2 and message.command[1] in ["subscribe", "error", "okay", "help"]:
        buttons = [[
            InlineKeyboardButton('sᴜʀᴘʀɪsᴇ', callback_data='start')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.SUR_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return
    data = message.command[1]
    try:
        pre, file_id = data.split('_', 1)
    except ValueError:
        file_id = data
        pre = ""
    if data.split("-", 1)[0] == "BATCH":
        sts = await message.reply("Please wait")
        file_id = data.split("-", 1)[1]
        msgs = BATCH_FILES.get(file_id)
        if not msgs:
            file = await client.download_media(file_id)
            try: 
                with open(file, 'r') as file_data:
                    msgs = json.loads(file_data.read())
            except Exception as e:
                await sts.edit("FAILED")
                return await client.send_message(LOG_CHANNEL, "UNABLE TO OPEN FILE.")
            os.remove(file)
            BATCH_FILES[file_id] = msgs
        for msg in msgs:
            title = msg.get("title")
            size = get_size(int(msg.get("size", 0)))
            f_caption = msg.get("caption", "")
            if BATCH_FILE_CAPTION:
                try:
                    f_caption = BATCH_FILE_CAPTION.format(file_name=title if title else '', file_size=size if size else '', file_caption=f_caption if f_caption else '')
                except Exception as e:
                    logger.exception(e)
                    f_caption = f_caption
            if f_caption is None:
                f_caption = f"{title}" if title else ""
            try:
                await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=msg.get("file_id"),
                    caption=f_caption,
                    protect_content=msg.get('protect', False),
                )
            except FloodWait as e:
                await asyncio.sleep(e.x)
                logger.warning(f"Floodwait of {e.x} sec.")
                await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=msg.get("file_id"),
                    caption=f_caption,
                    protect_content=msg.get('protect', False),
                )
            except Exception as e:
                logger.warning(e, exc_info=True)
                continue
            await asyncio.sleep(1) 
        await sts.delete()
        return
    elif data.split("-", 1)[0] == "DSTORE":
        sts = await message.reply("Please wait")
        b_string = data.split("-", 1)[1]
        decoded = (base64.urlsafe_b64decode(b_string + "=" * (-len(b_string) % 4))).decode("ascii")
        try:
            f_msg_id, l_msg_id, f_chat_id, protect = decoded.split("_", 3)
        except ValueError:
            f_msg_id, l_msg_id, f_chat_id = decoded.split("_", 2)
            protect = "/pbatch" if PROTECT_CONTENT else "batch"
        diff = int(l_msg_id) - int(f_msg_id)
        async for msg in client.iter_messages(int(f_chat_id), int(l_msg_id), int(f_msg_id)):
            if msg.media:
                media = getattr(msg, msg.media)
                if BATCH_FILE_CAPTION:
                    try:
                        f_caption = BATCH_FILE_CAPTION.format(file_name=getattr(media, 'file_name', ''), file_size=getattr(media, 'file_size', ''), file_caption=getattr(msg, 'caption', ''))
                    except Exception as e:
                        logger.exception(e)
                        f_caption = getattr(msg, 'caption', '')
                else:
                    media = getattr(msg, msg.media)
                    file_name = getattr(media, 'file_name', '')
                    f_caption = getattr(msg, 'caption', file_name)
                try:
                    await msg.copy(message.chat.id, caption=f_caption, protect_content=True if protect == "/pbatch" else False)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    await msg.copy(message.chat.id, caption=f_caption, protect_content=True if protect == "/pbatch" else False)
                except Exception as e:
                    logger.exception(e)
                    continue
            elif msg.empty:
                continue
            else:
                try:
                    await msg.copy(message.chat.id, protect_content=True if protect == "/pbatch" else False)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    await msg.copy(message.chat.id, protect_content=True if protect == "/pbatch" else False)
                except Exception as e:
                    logger.exception(e)
                    continue
            await asyncio.sleep(1) 
        await sts.delete()
    
    files_ = await get_file_details(file_id)           
    if not files_:
        pre, file_id = ((base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))).decode("ascii")).split("_", 1)
        try:
            msg = await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file_id,
                protect_content=True if pre == 'filep' else False,
            )
            filetype = msg.media
            file = getattr(msg, filetype)
            title = file.file_name
            size = get_size(file.file_size)
            f_caption = f"<code>{title}</code>"
            if CUSTOM_FILE_CAPTION:
                try:
                    f_caption = CUSTOM_FILE_CAPTION.format(file_name=title if title else '', file_size=size if size else '', file_caption='')
                except:
                    return
            await msg.edit_caption(f_caption)
            return
        except:
            pass
        return await message.reply('No such file exists.')
    
    files = files_[0]
    title = files.file_name
    size = get_size(files.file_size)
    f_caption = files.caption
    if CUSTOM_FILE_CAPTION:
        try:
            f_caption = CUSTOM_FILE_CAPTION.format(file_name=title if title else '', file_size=size if size else '', file_caption='' if f_caption is None else f_caption)
        except Exception as e:
            logger.exception(e)
            f_caption = f_caption
    if f_caption is None:
        f_caption = f"{files.file_name}"
    await client.send_cached_media(
        chat_id=message.from_user.id,
        file_id=file_id,
        caption=f_caption,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton('ᴊᴏɪɴ ᴛᴏ ᴄʜᴀɴɴᴇʟ', url=MAIN_CHANNEL)
                ]
            ]
        ),
        protect_content=True if pre == 'filep' else False,
    )
    
@Client.on_message(filters.command('channel') & filters.user(ADMINS))
async def channel_info(bot, message):
    if isinstance(CHANNELS, (int, str)):
        channels = [CHANNELS]
    elif isinstance(CHANNELS, list):
        channels = CHANNELS
    else:
        raise ValueError("Unexpected type of CHANNELS")

    text = '📑 **Indexed channels/groups**\n'
    for channel in channels:
        chat = await bot.get_chat(channel)
        text += f'\n👥 **Title:** {chat.title or chat.first_name}'
        text += f'\n🆔 **ID:** {chat.id}'
        if chat.username:
            text += f'\n🌐 **Username:** @{chat.username}'

    text += f'\n\n**Total:** {len(CHANNELS)}'

    if len(text) < 4096:
        await message.reply(text)
    else:
        file = 'Indexed_channels.txt'
        with open(file, 'w') as f:
            f.write(text)
        await message.reply_document(file)
        os.remove(file)

@Client.on_message(filters.command('logs') & filters.user(ADMINS))
async def log_file(bot, message):
    try:
        with open('TelegramBot.log', 'rb') as log_file:
            await bot.send_document(chat_id=message.chat.id, document=log_file, caption='📜 Log file')
    except Exception as e:
        await message.reply(str(e))
        
@Client.on_message(filters.command('delete') & filters.user(ADMINS))
async def delete(bot, message):
    reply = message.reply_to_message
    if reply and reply.media:
        msg = await message.reply("Processing...⏳", quote=True)
    else:
        await message.reply('Reply to a file with /delete to delete it.', quote=True)
        return

    supported_types = ["document", "video", "audio"]
    media = None

    for file_type in supported_types:
        media = getattr(reply, file_type, None)
        if media:
            break

    if not media:
        await msg.edit('This is not a supported file format.')
        return

    file_id, file_ref = unpack_new_file_id(media.file_id)

    result = await Media.collection.delete_one({
        '_id': file_id,
    })

    if result.deleted_count:
        await msg.edit('File is successfully deleted from the database')
        # Send a log message to the DELETE_LOG channel
        await bot.send_message(LOG_CHANNEL, f'File deleted: {media.file_name} by {message.from_user.mention}')
    else:
        file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
        result = await Media.collection.delete_many({
            'file_name': file_name,
            'file_size': media.file_size,
            'mime_type': media.mime_type
        })

        if result.deleted_count:
            await msg.edit('File is successfully deleted from the database')
            # Send a log message to the DELETE_LOG channel
            await bot.send_message(LOG_CHANNEL, f'File deleted: {media.file_name} by {message.from_user.mention}')
        else:
            result = await Media.collection.delete_many({
                'file_name': media.file_name,
                'file_size': media.file_size,
                'mime_type': media.mime_type
            })

            if result.deleted_count:
                await msg.edit('File is successfully deleted from the database')
                # Send a log message to the DELETE_LOG channel
                await bot.send_message(LOG_CHANNEL, f'File deleted: {media.file_name} by {message.from_user.mention}')
            else:
                await msg.edit('File not found in the database')

@Client.on_message(filters.command('deleteall') & filters.user(ADMINS))
async def delete_all_index(bot, message):
    confirmation_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="YES", callback_data="autofilter_delete"),
                InlineKeyboardButton(text="CANCEL", callback_data="close_data"),
            ],
        ]
    )
    await message.reply_text(
        'This will delete all indexed files. Do you want to continue?',
        reply_markup=confirmation_markup,
        quote=True,
    )

@Client.on_callback_query(filters.regex(r'^autofilter_delete'))
async def delete_all_index_confirm(bot, message):
    await Media.collection.drop()
    await message.answer(MSG_ALRT)
    await message.message.edit('Successfully Deleted All The Indexed Files.')

@Client.on_message(filters.command('settings'))
async def settings(client, message):
    user_id = message.from_user.id if message.from_user else None

    if not user_id:
        return await message.reply(f"You are an anonymous admin. Use /connect {message.chat.id} in PM")

    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        group_id = await active_connection(str(user_id))

        if group_id is not None:
            try:
                chat = await client.get_chat(group_id)
                title = chat.title
            except:
                await message.reply_text("Make sure I'm present in your group!!", quote=True)
                return
        else:
            await message.reply_text("I'm not connected to any groups!", quote=True)
            return

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        group_id = message.chat.id
        title = message.chat.title

    else:
        return

    member_status = await client.get_chat_member(group_id, user_id).status

    if (
            member_status != enums.ChatMemberStatus.ADMINISTRATOR
            and member_status != enums.ChatMemberStatus.OWNER
            and str(user_id) not in ADMINS
    ):
        return

    settings = await get_settings(group_id)

    if settings is not None:
        buttons = [
            [
                InlineKeyboardButton('Filter Button', callback_data=f'setgs#button#{settings["button"]}#{str(grpid)}'),
                InlineKeyboardButton('Single' if settings["button"] else 'Double', callback_data=f'setgs#button#{settings["button"]}#{str(grpid)}')
            ],
            [
                InlineKeyboardButton('Redirect To', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grpid)}'),
                InlineKeyboardButton('Bot PM' if settings["botpm"] else 'Channel', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grpid)}')
            ],
            [
                InlineKeyboardButton('File Secure', callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grpid)}'),
                InlineKeyboardButton('✅ Yes' if settings["file_secure"] else '❌ No', callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grpid)}')
            ],
            [
                InlineKeyboardButton('IMDB', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grpid)}'),
                InlineKeyboardButton('✅ Yes' if settings["imdb"] else '❌ No', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grpid)}')
            ],
            [
                InlineKeyboardButton('Spell Check', callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grpid)}'),
                InlineKeyboardButton('✅ Yes' if settings["spell_check"] else '❌ No', callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grpid)}')
            ],
            [
                InlineKeyboardButton('Welcome', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grpid)}'),
                InlineKeyboardButton('✅ Yes' if settings["welcome"] else '❌ No', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grpid)}')
            ],
            [
                InlineKeyboardButton('Auto Delete', callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grpid)}'),
                InlineKeyboardButton('10 Mins' if settings["auto_delete"] else 'OFF', callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grpid)}')
            ],
            [
                InlineKeyboardButton('ShortLink', callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grpid)}'),
                InlineKeyboardButton('✅ ON' if settings["is_shortlink"] else '❌ OFF', callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grpid)}')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_text(
            text=f"<b>Change Your Settings for {title} As You Wish ⚙</b>",
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML,
            reply_to_message_id=message.id
        )

@Client.on_message(filters.command('set_template'))
async def save_template(client, message):
    user_id = message.from_user.id if message.from_user else None

    if not user_id:
        return await message.reply(f"You are an anonymous admin. Use /connect {message.chat.id} in PM")

    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        group_id = await active_connection(str(user_id))

        if group_id is not None:
            try:
                chat = await client.get_chat(group_id)
                title = chat.title
            except:
                await message.reply_text("Make sure I'm present in your group!!", quote=True)
                return
        else:
            await message.reply_text("I'm not connected to any groups!", quote=True)
            return

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        group_id = message.chat.id
        title = message.chat.title

    else:
        return

    member_status = await client.get_chat_member(group_id, user_id).status

    if (
            member_status != enums.ChatMemberStatus.ADMINISTRATOR
            and member_status != enums.ChatMemberStatus.OWNER
            and str(user_id) not in ADMINS
    ):
        return

    if len(message.command) < 2:
        return await message.reply("No Input!!")

    template = message.text.split(" ", 1)[1]
    await save_group_settings(group_id, 'template', template)
    await message.reply(f"Successfully changed template for {title} to\n\n{template}")

@Client.on_message(filters.command("deletefiles") & filters.user(ADMINS))
async def deletemultiplefiles(bot, message):
    btn = [
        [
            InlineKeyboardButton("Delete PreDVDs", callback_data="predvd"),
            InlineKeyboardButton("Delete CamRips", callback_data="camrip"),
        ],
        [
            InlineKeyboardButton("Delete HDCams", callback_data="hdcam"),
            InlineKeyboardButton("Delete S-Prints", callback_data="sprint"),
        ],
        [
            InlineKeyboardButton("Delete HDTVRip", callback_data="hdtvrip"),
            InlineKeyboardButton("Cancel", callback_data="cancel"),
        ],
    ]
    await message.reply_text(
        text="<b>Select the type of files you want to delete!\n\nThis will delete 100 files from the database for the selected type.</b>",
        reply_markup=InlineKeyboardMarkup(btn)
    )

@Client.on_message(filters.command("send") & filters.user(ADMINS))
async def send_msg(bot, message):
    if not message.reply_to_message:
        await message.reply_text("<b>Use this command as a reply to any message using the target chat id. For example: /send userid</b>")
        return

    target_id = message.text.split(" ", 1)[1]
    out = "Users Saved In DB Are:\n\n"
    success = False

    try:
        user = await bot.get_users(target_id)
        users = await db.get_all_users()

        for usr in users:
            out += f"{usr['id']}\n"

        if str(user.id) in out:
            await message.reply_to_message.copy(int(user.id))
            success = True
        else:
            success = False

        if success:
            await message.reply_text(f"<b>Your message has been successfully sent to {user.mention}.</b>")
        else:
            await message.reply_text("<b>This user hasn't started this bot yet!</b>")
    except Exception as e:
        await message.reply_text(f"<b>Error: {e}</b>")
        
@Client.on_message(filters.command("shortlink") & filters.user(ADMINS))
async def shortlink(bot, message):
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        return await message.reply_text(f"<b>Hey {message.from_user.mention}, This command only works in groups!</b>")
    
    grpid = message.chat.id
    title = message.chat.title
    
    data = message.text.split()
    
    if len(data) != 3:
        return await message.reply_text("<b>Command Incomplete :(\n\nGive me a shortlink and API along with the command!\n\nFormat: <code>/shortlink shorturl.in 95a8195c40d31e0c3b6baa68813fcecb1239f2e9</code></b>")
    
    command, shortlink_url, api = data

    userid = message.from_user.id
    user = await bot.get_chat_member(grpid, userid)

    if user.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER] and str(userid) not in ADMINS:
        return await message.reply_text("<b>You don't have access to use this command!</b>")

    reply = await message.reply_text("<b>Please Wait...</b>")
    
    await save_group_settings(grpid, 'shortlink', shortlink_url)
    await save_group_settings(grpid, 'shortlink_api', api)
    await save_group_settings(grpid, 'is_shortlink', True)
    
    await reply.edit_text(f"<b>Successfully added shortlink API for {title}.\n\nCurrent Shortlink Website: <code>{shortlink_url}</code>\nCurrent API: <code>{api}</code></b>")
