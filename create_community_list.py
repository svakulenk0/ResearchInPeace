#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on Mar 29, 2016

.. codeauthor: svitlana vakulenko
    <svitlana.vakulenko@gmail.com>

Step 1. Start out with a set of seed keywords, e.g. hashtags for CS conferences.
Step 2. Add all users who tweeted using these hashtags to a public Twitter list.

'''

from twython import Twython, TwythonRateLimitError

from settings import *
from twitter_settings import *
from twitter_search import exhaustive_search


class Twitter_Processor():
    def __init__(self):
        self.twitter_client = self.connect_to_twitter()
        self.community_members = set()

    def connect_to_twitter(self):
        return Twython(APP_KEY, APP_SECRET,
                       OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

    def delete_list(self, list_name):
        self.twitter_client.delete_list(slug=list_name,
                                        owner_screen_name=MY_NAME)

    def retrieve_my_lists(self):
        return self.twitter_client.show_lists(screen_name=MY_NAME)


def follow_communities_from_mongo(db_name, collection_name, lists=COMMUNITIES):
    mongo = Mongo_Connector(db_name, collection_name)
    for community, keywords in lists.iteritems():
        for keyword in keywords:
            users = mongo.get_users_from_mongo(keyword)
            print "Found " + str(len(users)) + " users in " + keyword
            TP = Twitter_Processor()
            try:
                TP.add_to_list(users, list_name=community)
            except Exception as e:
                print e
                pass


def follow_users_from_mongo(db_name, collection_name, lists=MY_LISTS):
    mongo = Mongo_Connector(db_name, collection_name)
    for keyword in lists:
        users = mongo.get_users_from_mongo(keyword)
        print "Found " + str(len(users)) + " users in " + keyword
        TP = Twitter_Processor()
        try:
            TP.add_to_list(users, list_name=keyword.replace(" ", ""))
        except Exception as e:
            print e
            pass


def drop_my_empty_lists():
    TP = Twitter_Processor()
    lists = TP.retrieve_my_lists()
    for twitter_list in lists:
        list_name = twitter_list['slug']
        list_size = twitter_list['member_count']
        print list_name, list_size
        if list_size < 2:
            # delete the list by name
            TP.delete_list(list_name)


def collect_new_users(collection, db_name, load_tweets=True,
                      keywords=KEYWORDS):
    # 1st get new tweets
    if load_tweets:
        for keyword in keywords:
            # recent week results only due to the Twitter API restriction
            exhaustive_search(keyword, db_name, collection)
    # 2nd add new users
    follow_users_from_mongo(db_name, collection)
    follow_communities_from_mongo(db_name, collection)
    # 3rd TODO check why empty lists are created
    drop_my_empty_lists()


def maintain_my_community_lists(collection=COLLECTION, db_name=DB_NAME):
    collect_new_users(collection, db_name, load_tweets=True)


if __name__ == '__main__':
    maintain_my_community_lists()

