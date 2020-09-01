from pymongo import MongoClient
from bson.objectid import ObjectId
import urllib


class DB:

    def __init__(self):
        # client = MongoClient("mongodb+srv://pmalope:martian143281@matcha-2ordl.mongodb.net/test?retryWrites=true&w=majority",connect=False,) #connect to cloud mongodb
        client = MongoClient("mongodb://localhost:27017", connect=False, ) #connect to local mongodb
        #client = MongoClient("mongodb://mongo:27017", connect=False, ) #connect mongodb container
        db = client['Matcha']
        self.__users = db['users']
        self.__chats = db['chats']

    def get_user(self, query, fields=None):
        if not fields:
            user = self.__users.find_one(query)
        else:
            user = self.__users.find_one(query, fields)

        return user

    def register_user(self, user_info):
        self.__users.insert_one(user_info)

    def users(self, query={}):
        return self.__users.find(query)

    def count_users(self):
        return self.__users.count_documents({})

    def update_user(self, user_id, values):
        items = values.items()
        for key, value in items:
            if key == '_id':
                continue
            self.__users.update_one({'_id': user_id}, {'$set': {key: value}})

    def update_likes(self, user_id, change):
        query = {'_id': user_id}
        new_values = {'$set': change}

        self.__users.update_one(query, new_values)

    def create_history(self, room):
        history = {
            '_id': room,
            'chats': []
        }
        self.__chats.insert_one(history)

    def insert_chat(self, sender, room, message):
        history = self.get_chat(room)
        data = {sender: message}
        history['chats'].append(data)

        self.__chats.update_one({'_id': history['_id']}, {'$set': history})

    def get_chat(self, room):
        return self.__chats.find_one({'_id': room})
