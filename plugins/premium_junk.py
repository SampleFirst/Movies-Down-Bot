import time
import datetime
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid
from pyrogram.types import Message
from database.users_chats_db import db
from info import ADMINS

@Client.on_message(filters.command("premium_clear_junk") & filters.user(ADMINS))
async def remove_junk_premium_users_db(bot, message: Message):
    users = await db.get_all_premium_users()
    b_msg = message
    sts = await message.reply_text('Clearing junk premium users...')
    start_time = time.time()
    total_users = await db.total_premium_users_count()
    blocked = 0
    deleted = 0
    failed = 0
    done = 0
    async for user in users:
        pti, sh = await clear_junk_premium(int(user['id']), b_msg, bot)
        if not pti:
            if sh == "Blocked":
                blocked += 1
            elif sh == "Deleted":
                deleted += 1
            elif sh == "Error":
                failed += 1
        done += 1
        if not done % 20:
            await sts.edit(f"In progress:\n\nTotal Premium Users {total_users}\nCompleted: {done} / {total_users}\nBlocked: {blocked}\nDeleted: {deleted}")
    time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts.delete()
    await bot.send_message(message.chat.id, f"Completed:\nCompleted in {time_taken} seconds.\n\nTotal Premium Users {total_users}\nCompleted: {done} / {total_users}\nBlocked: {blocked}\nDeleted: {deleted}")

async def clear_junk_premium(user_id, message, bot):
    try:
        key = await message.copy(chat_id=user_id)
        await key.delete(True)
        return True, "Success"
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return await clear_junk_premium(user_id, message, bot)
    except InputUserDeactivated:
        await db.delete_premium_user(int(user_id))
        logging.info(f"{user_id} - Removed from Database, since deleted account.")
        return False, "Deleted"
    except UserIsBlocked:
        logging.info(f"{user_id} - Blocked the bot.")
        return False, "Blocked"
    except PeerIdInvalid:
        await db.delete_premium_user(int(user_id))
        logging.info(f"{user_id} - PeerIdInvalid")
        return False, "Error"
    except Exception as e:
        return False, "Error"
