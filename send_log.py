import asyncio
from datetime import datetime, date, timedelta
import pytz
from database.users_chats_db import db
from info import LOG_CHANNEL
from Script import script  

async def send_log(bot, interval):  # Pass 'bot' as the first argument
    while True:
        total_chats = await db.total_chat_count()
        total_users = await db.total_users_count()
        tz = pytz.timezone('Asia/Kolkata')
        now = datetime.now(tz)

        if interval == 'daily' and now.hour == 16 and now.minute == 5:
            # This code will execute at 11:50 PM for daily log
            today = date.today()
            time = now.strftime("%H:%M:%S %p")
            await bot.send_message(chat_id=LOG_CHANNEL, text=script.REPORT_TXT.format(a=total_chats, b=total_users, c=today, d=time))
            # Calculate time until the next day at 11:50 PM
            next_execution = datetime(now.year, now.month, now.day, 23, 50) + timedelta(days=1)
            sleep_time = (next_execution - now).total_seconds()
            await asyncio.sleep(sleep_time)

        elif interval == 'weekly' and now.weekday() == 6 and now.hour == 23 and now.minute == 59:
            # This code will execute at 11:59 PM on Sundays for weekly log
            today = date.today()
            time = now.strftime("%H:%M:%S %p")
            await bot.send_message(chat_id=LOG_CHANNEL, text=script.REPORT_TXT.format(a=total_chats, b=total_users, c=today, d=time))
            # Calculate time until the next Sunday at 11:59 PM
            days_until_next_sunday = 6 - now.weekday() + 7  # 6 - weekday + 7 days to next Sunday
            next_execution = datetime(now.year, now.month, now.day, 23, 59) + timedelta(days=days_until_next_sunday)
            sleep_time = (next_execution - now).total_seconds()
            await asyncio.sleep(sleep_time)

        elif interval == 'monthly' and now.day == 1 and now.hour == 23 and now.minute == 59:
            # This code will execute at 11:59 PM on the 1st day of the month for monthly log
            today = date.today()
            time = now.strftime("%H:%M:%S %p")
            await bot.send_message(chat_id=LOG_CHANNEL, text=script.REPORT_TXT.format(a=total_chats, b=total_users, c=today, d=time))
            # Calculate time until the next month on the 1st at 11:59 PM
            next_execution = datetime(now.year, now.month + 1, 1, 23, 59)
            sleep_time = (next_execution - now).total_seconds()
            await asyncio.sleep(sleep_time)

        else:
            # Sleep for 5 minute and check again
            await asyncio.sleep(300)
