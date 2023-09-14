import asyncio
from datetime import datetime, date
import pytz
from database.users_chats_db import db
from info import LOG_CHANNEL
from Script import script
from utils import temp

async def send_log(bot, interval):
    while True:
        tz = pytz.timezone('Asia/Kolkata')
        now = datetime.now(tz)

        if interval == 'daily' and now.hour == 23 and now.minute == 59:
            today = date.today()
            total_users = await db.total_users_count()
            daily_users = await db.daily_users_count(today) + 1
            total_chats = await db.total_chat_count()
            daily_chats = await db.daily_chats_count(today) + 1
            time = now.strftime("%H:%M:%S %p")
            day_name = today.strftime("%A")

            await bot.send_message(chat_id=LOG_CHANNEL, text=script.REPORT_DAY_TXT.format(
                a=temp.U_NAME, 
                b=today, 
                c=day_name, 
                d=time, 
                e=total_users, 
                g=daily_users, 
                h=total_chats, 
                i=daily_chats))
            await asyncio.sleep(300)

        elif interval == 'weekly' and now.weekday() == 6 and now.hour == 0 and now.minute == 0:
            today = date.today()
            total_users = await db.total_users_count()
            daily_users = await db.daily_users_count(today) + 1
            total_chats = await db.total_chat_count()
            daily_chats = await db.daily_chats_count(today) + 1
            time = now.strftime("%H:%M:%S %p")
            day_name = today.strftime("%A")

            await bot.send_message(chat_id=LOG_CHANNEL, text=script.REPORT_WEEK_TXT.format(
                a=temp.U_NAME, 
                b=today, 
                c=day_name, 
                d=time, 
                e=total_users, 
                g=daily_users, 
                h=total_chats, 
                i=daily_chats))
            await asyncio.sleep(300)

        elif interval == 'monthly' and now.day == 1 and now.hour == 0 and now.minute == 1:
            today = date.today()
            total_users = await db.total_users_count()
            daily_users = await db.daily_users_count(today) + 1
            total_chats = await db.total_chat_count()
            daily_chats = await db.daily_chats_count(today) + 1
            time = now.strftime("%H:%M:%S %p")
            month = now.strftime("%B")
            day_name = today.strftime("%A")

            await bot.send_message(chat_id=LOG_CHANNEL, text=script.REPORT_MONTH_TXT.format(
                a=temp.U_NAME, 
                b=today, 
                c=day_name, 
                d=month, 
                e=time, 
                g=total_users, 
                h=daily_users, 
                i=total_chats, 
                j=daily_chats))
            await asyncio.sleep(300)

        else:
            await asyncio.sleep(300)
            
