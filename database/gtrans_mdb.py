import pymongo
from info import DATABASE_URI, DATABASE_NAME
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

myclient = pymongo.MongoClient(DATABASE_URI)
mydb = myclient[DATABASE_NAME]
mycol = mydb["USER"]

def insert(chat_id):
    user_id = int(chat_id)
    user_det = {"_id": user_id, "lg_code": None}
    try:
        mycol.insert_one(user_det)
    except Exception as e:
        logger.exception('Error occurred while inserting data!', exc_info=True)

def set(chat_id, lg_code):
    try:
        mycol.update_one({"_id": chat_id}, {"$set": {"lg_code": lg_code}})
    except Exception as e:
        logger.exception('Error occurred while updating data!', exc_info=True)

def unset(chat_id):
    try:
        mycol.update_one({"_id": chat_id}, {"$set": {"lg_code": None}})
    except Exception as e:
        logger.exception('Error occurred while unsetting data!', exc_info=True)

def find(chat_id):
    id = {"_id": chat_id}
    x = mycol.find(id)
    for i in x:
        lgcd = i.get("lg_code")
        return lgcd

def getid():
    values = []
    try:
        for key in mycol.find():
            id = key["_id"]
            values.append(id)
    except Exception as e:
        logger.exception('Error occurred while getting IDs!', exc_info=True)
    return values

def find_one(id):
    try:
        return mycol.find_one({"_id": id})
    except Exception as e:
        logger.exception('Error occurred while finding one!', exc_info=True)
