import pytz
from datetime import date, datetime
import motor.motor_asyncio
from info import DATABASE_NAME, DATABASE_URI, IMDB, IMDB_TEMPLATE, MELCOW_NEW_USERS, P_TTI_SHOW_OFF, SINGLE_BUTTON, SPELL_CHECK_REPLY, PROTECT_CONTENT, AUTO_DELETE, SHORTLINK_API, SHORTLINK_URL, IS_SHORTLINK, RULS_ON

class Database:
    
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.grp = self.db.groups


    def new_user(self, id, name):
        tz = pytz.timezone('Asia/Kolkata')  # Define tz here
        return dict(
            id=id,
            name=name,
            ban_status=dict(
                is_banned=False,
                ban_reason="",
            ),
            timestamp=datetime.now(tz)
        )

    def new_group(self, id, title, username):
        tz = pytz.timezone('Asia/Kolkata')  # Define tz here
        return dict(
            id=id,
            title=title,
            username=username,
            chat_status=dict(
                is_disabled=False,
                reason="",
            ),
            timestamp=datetime.now(tz)
        )

    async def daily_users_count(self, today):
        tz = pytz.timezone('Asia/Kolkata')
        start = tz.localize(datetime.combine(today, datetime.min.time()))
        end = tz.localize(datetime.combine(today, datetime.max.time()))
        count = await self.col.count_documents({
            'timestamp': {'$gte': start, '$lt': end}
        })
        return count
    
    
    async def daily_chats_count(self, today):
        tz = pytz.timezone('Asia/Kolkata')
        start = tz.localize(datetime.combine(today, datetime.min.time()))
        end = tz.localize(datetime.combine(today, datetime.max.time()))
        count = await self.grp.count_documents({
            'timestamp': {'$gte': start, '$lt': end}
        })
        return count
    
    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)
    
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id':int(id)})
        return bool(user)
    
    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count
    
    async def remove_ban(self, id):
        ban_status = dict(
            is_banned=False,
            ban_reason=''
        )
        await self.col.update_one({'id': id}, {'$set': {'ban_status': ban_status}})
    
    async def ban_user(self, user_id, ban_reason="No Reason"):
        ban_status = dict(
            is_banned=True,
            ban_reason=ban_reason
        )
        await self.col.update_one({'id': user_id}, {'$set': {'ban_status': ban_status}})

    async def get_ban_status(self, id):
        default = dict(
            is_banned=False,
            ban_reason=''
        )
        user = await self.col.find_one({'id':int(id)})
        if not user:
            return default
        return user.get('ban_status', default)

    async def get_all_users(self):
        return self.col.find({})
    

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})


    async def get_banned(self):
        users = self.col.find({'ban_status.is_banned': True})
        chats = self.grp.find({'chat_status.is_disabled': True})
        b_chats = [chat['id'] async for chat in chats]
        b_users = [user['id'] async for user in users]
        return b_users, b_chats
    


    async def add_chat(self, chat, title, username):
        chat = self.new_group(chat, title, username)
        await self.grp.insert_one(chat)
    

    async def get_chat(self, chat):
        chat = await self.grp.find_one({'id':int(chat)})
        return False if not chat else chat.get('chat_status')
    

    async def re_enable_chat(self, id):
        chat_status=dict(
            is_disabled=False,
            reason="",
            )
        await self.grp.update_one({'id': int(id)}, {'$set': {'chat_status': chat_status}})
        
    async def update_settings(self, id, settings):
        await self.grp.update_one({'id': int(id)}, {'$set': {'settings': settings}})
        
    
    async def get_settings(self, id):
        default = {
            'button': SINGLE_BUTTON,
            'botpm': P_TTI_SHOW_OFF,
            'file_secure': PROTECT_CONTENT,
            'imdb': IMDB,
            'spell_check': SPELL_CHECK_REPLY,
            'welcome': MELCOW_NEW_USERS,
            'auto_delete': AUTO_DELETE,
            'template': IMDB_TEMPLATE,
            'shortlink': SHORTLINK_URL,
            'shortlink_api': SHORTLINK_API,
            'is_shortlink': IS_SHORTLINK,
            'ruls_on': RULS_ON
    
        }
        chat = await self.grp.find_one({'id':int(id)})
        if chat:
            return chat.get('settings', default)
        return default
    

    async def disable_chat(self, chat, reason="No Reason"):
        chat_status=dict(
            is_disabled=True,
            reason=reason,
            )
        await self.grp.update_one({'id': int(chat)}, {'$set': {'chat_status': chat_status}})
    

    async def total_chat_count(self):
        count = await self.grp.count_documents({})
        return count
    

    async def get_all_chats(self):
        return self.grp.find({})


    async def get_db_size(self):
        return (await self.db.command("dbstats"))['dataSize']

    async def save_chat_invite_link(self, chat_id, invite_link):
        await self.grp.update_one({'id': int(chat_id)}, {'$set': {'invite_link': invite_link}})
    
    async def get_chat_invite_link(self, chat_id):
        chat = await self.grp.find_one({'id': int(chat_id)})
        if chat:
            return chat.get('invite_link', None)
        return None

db = Database(DATABASE_URI, DATABASE_NAME)

