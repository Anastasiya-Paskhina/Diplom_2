from pymongo import MongoClient


class DataBase:
    def __init__(self, host='localhost',
                 port=27017, username=None,
                 password=None):
        client = MongoClient(host=host,
                             port=port,
                             username=username,
                             password=password)
        users_db = client.vk_users
        self.db = users_db

    def add(self, data):
        users_list = self.db.users_list
        users_list.insert_many(data)

    def check(self, value):
        res = list(self.db.users_list.find({'user_id': value}))
        return len(res) == 0