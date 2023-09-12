# Standard Library Imports
import asyncio
from datetime import datetime

# Pyrogram Library Imports
from pyrogram.errors import ChatAdminRequired
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong, PeerIdInvalid

# Database Imports
from database.users_chats_db import db
from database.ia_filterdb import Media

# Local Imports
from utils import get_size, temp, get_settings
from Script import script

# Environment Variables
from info import(
    ADMINS, 
    LOG_CHANNEL, 
    SUPPORT_CHAT, 
    MELCOW_NEW_USERS, 
    MELCOW_IMG, 
    MELCOW_VID, 
    MAIN_CHANNEL, 
    S_GROUP
)


@Client.on_message(filters.new_chat_members & filters.group)
async def save_group(bot, message):
    new_members = message.new_chat_members
    if bot.get_me().id in [user.id for user in new_members]:
        if not await db.get_chat(message.chat.id):
            total_members = await bot.get_chat_members_count(message.chat.id)
            referrer = message.from_user.mention if message.from_user else "Anonymous"
            await bot.send_message(LOG_CHANNEL, f"New group: {message.chat.title} ({message.chat.id}), Members: {total_members}, Referrer: {referrer}")
            await db.add_chat(message.chat.id, message.chat.title)

        if message.chat.id in temp.BANNED_CHATS:
            buttons = [[
                InlineKeyboardButton('Support', url=f'https://t.me/{SUPPORT_CHAT}')
            ]]
            reply_markup = InlineKeyboardMarkup(buttons)
            message_text = '<b>CHAT NOT ALLOWED 🐞\n\nMy admins have restricted me from working here! If you want to know more about it, contact support.</b>'
            sent_message = await message.reply(
                text=message_text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )

            try:
                await sent_message.pin()
            except Exception as e:
                print(e)

            await bot.leave_chat(message.chat.id)
            return

        buttons = [[
            InlineKeyboardButton('ℹ️ Help', url=f"https://t.me/{temp.U_NAME}?start=help"),
            InlineKeyboardButton('📢 Updates', url=MAIN_CHANNEL)
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)

        welcome_message = f"<b>Thank you for adding me to {message.chat.title} ❣️\n\nIf you have any questions or doubts about using me, contact support.</b>"
        await message.reply_text(
            text=welcome_message,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    else:
        settings = await get_settings(message.chat.id)
        if settings["welcome"]:
            for new_member in new_members:
                if temp.MELCOW.get('welcome') is not None:
                    try:
                        await temp.MELCOW['welcome'].delete()
                    except Exception as e:
                        print(e)

                welcome_message = script.MELCOW_ENG.format(new_member.mention, message.chat.title)
                temp.MELCOW['welcome'] = await message.reply_photo(
                    photo=MELCOW_IMG,
                    caption=welcome_message,
                    reply_markup=InlineKeyboardMarkup(
                        [[
                            InlineKeyboardButton('Support Group', url=S_GROUP),
                            InlineKeyboardButton('Updates Channel', url=MAIN_CHANNEL)
                        ]]
                    ),
                    parse_mode='HTML'
                )

        if settings["auto_delete"]:
            await asyncio.sleep(600)
            await temp.MELCOW['welcome'].delete()


@Client.on_message(filters.new_chat_members & filters.group)
async def welcome(bot, message):
    chat_id = message.chat.id
    group_name = message.chat.title
    username = message.from_user.username if message.from_user else None
    user_id = message.from_user.id if message.from_user else None

    if await db.get_chat(message.chat.id):
        total_members = await bot.get_chat_members_count(message.chat.id)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_text = f"#NEWMEMBER\nTime: {current_time}\nGroup Name: {group_name}\n"

        if username:
            log_text += f"Username: {username}\n"
        if user_id:
            log_text += f"User ID: {user_id}\n"
        log_text += f"Total Members: {total_members}"

        await bot.send_message(LOG_CHANNEL, text=log_text)


@Client.on_message(filters.left_chat_member)
async def goodbye(bot, message):
    chat_id = message.chat.id
    group_name = message.chat.title
    username = message.from_user.username if message.from_user else None
    user_id = message.from_user.id if message.from_user else None

    if await db.get_chat(message.chat.id):
        total_members = await bot.get_chat_members_count(message.chat.id)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_text = f"#LEFTMEMBER\nTime: {current_time}\nGroup Name: {group_name}\n"

        if username:
            log_text += f"Username: {username}\n"
        if user_id:
            log_text += f"User ID: {user_id}\n"
        log_text += f"Total Members: {total_members}"

        await bot.send_message(LOG_CHANNEL, text=log_text)


@Client.on_message(filters.command('leave') & filters.user(ADMINS))
async def leave_a_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')

    chat_id = message.command[1]

    try:
        chat_id = int(chat_id)
    except ValueError:
        pass

    try:
        buttons = [[
            InlineKeyboardButton('Support', url=f'https://t.me/{SUPPORT_CHAT}')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)

        await bot.send_message(
            chat_id=chat_id,
            text='<b>Hello Friends, \nMy admin has told me to leave from this group, so I am leaving! If you want to add me again, please contact my support group.</b>',
            reply_markup=reply_markup,
            parse_mode='HTML'
        )

        await bot.leave_chat(chat_id)
        await message.reply(f"Left the chat `{chat_id}`")
    except Exception as e:
        await message.reply(f'Error - {e}')


@Client.on_message(filters.command('disable') & filters.user(ADMINS))
async def disable_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')

    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason provided"

    try:
        chat_id = int(chat)
    except ValueError:
        return await message.reply('Give me a valid chat ID')

    chat_info = await db.get_chat(chat_id)

    if not chat_info:
        return await message.reply("Chat not found in the database")

    if chat_info['is_disabled']:
        return await message.reply(f"This chat is already disabled:\nReason: <code>{chat_info['reason']}</code>")

    await db.disable_chat(chat_id, reason)
    temp.BANNED_CHATS.append(chat_id)

    await message.reply('Chat successfully disabled')

    try:
        buttons = [[
            InlineKeyboardButton('Support', url=f'https://t.me/{SUPPORT_CHAT}')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await bot.send_message(
            chat_id=chat_id,
            text=f'<b>Hello friends,\nMy admin has disabled me in this group, so I am leaving! If you want to add me again, please contact my support group.</b>\nReason: <code>{reason}</code>',
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        await bot.leave_chat(chat_id)
    except Exception as e:
        await message.reply(f"Error - {e}")


@Client.on_message(filters.command('enable') & filters.user(ADMINS))
async def re_enable_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')

    chat_id = message.command[1]

    try:
        chat_id = int(chat_id)
    except ValueError:
        return await message.reply('Give me a valid chat ID')

    chat_info = await db.get_chat(chat_id)

    if not chat_info:
        return await message.reply("Chat not found in the database")

    if not chat_info.get('is_disabled'):
        return await message.reply('This chat is not disabled.')

    await db.re_enable_chat(chat_id)
    temp.BANNED_CHATS.remove(chat_id)

    await message.reply("Chat successfully re-enabled")


@Client.on_message(filters.command('stats') & filters.incoming)
async def get_ststs(bot, message):
    stat = await message.reply('Fetching stats..')
    total_users = await db.total_users_count()
    totl_chats = await db.total_chat_count()
    files = await Media.count_documents()
    size = await db.get_db_size()
    free = 536870912 - size
    size = get_size(size)
    free = get_size(free)
    await stat.edit(script.STATUS_TXT.format(files, total_users, totl_chats, size, free))


@Client.on_message(filters.command('invite') & filters.user(ADMINS))
async def gen_invite(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')

    chat_id = message.command[1]

    try:
        chat_id = int(chat_id)
    except ValueError:
        return await message.reply('Give me a valid chat ID')

    try:
        link = await bot.create_chat_invite_link(chat_id)
    except ChatAdminRequired:
        return await message.reply("Invite link generation failed. I do not have sufficient rights.")
    except Exception as e:
        return await message.reply(f'Error: {e}')

    await message.reply(f'Here is your invite link: {link.invite_link}')
    
    
@Client.on_message(filters.command('ban') & filters.user(ADMINS))
async def ban_a_user(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a user id / username')

    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        user_input = message.text.split(None, 2)[1]
    else:
        user_input = message.command[1]
        reason = "No reason provided"

    try:
        user = await bot.get_users(user_input)
    except PeerIdInvalid:
        return await message.reply("This is an invalid user. Make sure I have met them before.")
    except IndexError:
        return await message.reply("This might be a channel. Make sure it's a user.")
    except Exception as e:
        return await message.reply(f'Error - {e}')

    ban_status = await db.get_ban_status(user.id)
    if ban_status['is_banned']:
        return await message.reply(f"{user.mention} is already banned\nReason: {ban_status['ban_reason']}")

    await db.ban_user(user.id, reason)
    temp.BANNED_USERS.append(user.id)
    await message.reply(f"Successfully banned {user.mention}")


@Client.on_message(filters.command('unban') & filters.user(ADMINS))
async def unban_a_user(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a user id / username')

    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        user_input = message.text.split(None, 2)[1]
    else:
        user_input = message.command[1]
        reason = "No reason provided"

    try:
        user = await bot.get_users(user_input)
    except PeerIdInvalid:
        return await message.reply("This is an invalid user. Make sure I have met them before.")
    except IndexError:
        return await message.reply("This might be a channel. Make sure it's a user.")
    except Exception as e:
        return await message.reply(f'Error - {e}')

    ban_status = await db.get_ban_status(user.id)
    if not ban_status['is_banned']:
        return await message.reply(f"{user.mention} is not yet banned.")

    await db.remove_ban(user.id)
    temp.BANNED_USERS.remove(user.id)
    await message.reply(f"Successfully unbanned {user.mention}")


@Client.on_message(filters.command('users') & filters.user(ADMINS))
async def list_users(bot, message):
    try:
        raju = await message.reply('Getting List Of Users')
        users = await db.get_all_users()
        out = "Users Saved In DB Are:\n\n"
        for user in users:
            out += f"<a href='tg://user?id={user['id']}'>{user['name']}</a>"
            if user['ban_status']['is_banned']:
                out += ' (Banned User)'
            out += '\n'
    
        await raju.edit_text(out, parse_mode='HTML')
    except MessageTooLong:
        with open('users.txt', 'w+') as outfile:
            outfile.write(out)
        await message.reply_document('users.txt', caption="List Of Users")


@Client.on_message(filters.command('chats') & filters.user(ADMINS))
async def list_chats(bot, message):
    try:
        raju = await message.reply('Getting List Of Chats')
        chats = await db.get_all_chats()
        out = "Chats Saved In DB Are:\n\n"
        for chat in chats:
            out += f"**Title:** `{chat['title']}`\n**- ID:** `{chat['id']}`"
            if chat['chat_status']['is_disabled']:
                out += ' (Disabled Chat)'
            out += '\n'

        await raju.edit_text(out, parse_mode='Markdown')
    except MessageTooLong:
        with open('chats.txt', 'w+') as outfile:
            outfile.write(out)
        await bot.send_document(message.chat.id, 'chats.txt', caption="List Of Chats")
