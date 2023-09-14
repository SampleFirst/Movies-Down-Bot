import asyncio
from datetime import datetime, date
import pytz

async def send_log(self, interval):
    while True:
        total_chats = await db.total_chat_count()
        total_users = await db.total_users_count()
        tz = pytz.timezone('Asia/Kolkata')
        now = datetime.now(tz)
        
        if interval == 'daily' and now.hour == 15 and now.minute == 20:
            # This code will execute at 11:59 PM for daily log
            today = date.today()
            time = now.strftime("%H:%M:%S %p")
            await self.send_message(chat_id=LOG_CHANNEL, text=script.REPORT_TXT.format(a=total_chats, b=total_users, c=today, d=time))
            await asyncio.sleep(60)  # Sleep for 1 minute to avoid sending multiple messages

        elif interval == 'weekly' and now.weekday() == 6 and now.hour == 23 and now.minute == 59:
            # This code will execute at 11:59 PM on Sundays for weekly log
            today = date.today()
            time = now.strftime("%H:%M:%S %p")
            await self.send_message(chat_id=LOG_CHANNEL, text=script.REPORT_TXT.format(a=total_chats, b=total_users, c=today, d=time))
            await asyncio.sleep(60)  # Sleep for 1 minute to avoid sending multiple messages

        elif interval == 'monthly' and now.day == 1 and now.hour == 23 and now.minute == 59:
            # This code will execute at 11:59 PM on the 1st day of the month for monthly log
            today = date.today()
            time = now.strftime("%H:%M:%S %p")
            await self.send_message(chat_id=LOG_CHANNEL, text=script.REPORT_TXT.format(a=total_chats, b=total_users, c=today, d=time))
            await asyncio.sleep(60)  # Sleep for 1 minute to avoid sending multiple messages

        else:
            # Sleep for 1 minute and check again
            await asyncio.sleep(60)
            
