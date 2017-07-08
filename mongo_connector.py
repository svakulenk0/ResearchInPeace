#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient


class Mongo_Connector():

    def __init__(self, db_name, collection_name):
        # spin up database
        self.mongo_client = MongoClient()
        self.db = self.mongo_client[db_name]
        self.col = self.db[collection_name]

    def get_users_from_mongo(self, keyword, collect_mentions=False):
        '''
        2 categories of users collected: tweet authors and mentions in tweets
        '''
        #     unique users
        # keywords '$text': { '$search': keyword}
        # pipe = [{'$match': {'entities.hashtags.text': hashtag}},
        users1 = []
        if collect_mentions:
            pipe1 = [{'$match': {'$text': { '$search': keyword}}},
                	{'$group': {'_id': "$entities.user_mentions.screen_name"}}]  # users in mentions

            cursor1 = self.db.cs_conferences.aggregate(pipeline=pipe1)
            users1 = [user for user_mentions in cursor1 for user in user_mentions.values()[0]]
        # print users
        pipe2 = [{'$match': {'$text': { '$search': keyword}}},
                {'$group': {'_id': "$user.screen_name"}}]  # users as tweet authors

        cursor2 = self.db.cs_conferences.aggregate(pipeline=pipe2)
        users2 = [user.values()[0] for user in cursor2]
        return set(users2+users1)


def test_get_users_from_mongo():
    db_name = 'my_twitter'
    collection_name = 'cs_conferences'
    mongo = Mongo_Connector(db_name, collection_name)
    hashtag = "LREC2016"
    users = mongo.get_users_from_mongo(hashtag)
    print users


if __name__ == '__main__':
    test_get_users_from_mongo()
