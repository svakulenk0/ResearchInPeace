#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on Mar 29, 2016

.. codeauthor: svitlana vakulenko
    <svitlana.vakulenko@gmail.com>

Step 1. Start out with a set of seed keywords, e.g. hashtags for CS conferences.
Step 2. Add all users who tweeted using these hashtags to a public Twitter list.

'''

from twython import Twython

from settings import *
from twitter_settings import *
from twitter_search import exhaustive_search
from mongo_connector import Mongo_Connector


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

    def add_batch_to_list(self, list_name, batch):
        # concatenate user screen names for the query
        users_string = ",".join(batch)
        try:
            self.twitter_client.create_list_members(slug=list_name, owner_screen_name=MY_NAME, screen_name=users_string)
            print "Added " + str(len(batch)) + " new users to " + list_name
        except Exception, e:
            print e

    def unfriend(self, users):
        '''
        Input:
        users - list of screen_names
        '''
        for user in users:
            print user
            self.twitter_client.destroy_friendship(screen_name=user)

    def get_list_members(self, list_name):
        list_members = self.twitter_client.get_list_members(slug=list_name, owner_screen_name=MY_NAME,count=5000, skip_status=1)['users']
        print "Members in the list '" + list_name + "': " + str(len(list_members))
        return list_members

    def retrieve_friends_of(self, user_name=MY_NAME, limit=200):
        next_cursor = -1
        users = []
        result = self.twitter_client.get_friends_list(screen_name=user_name, count=limit, skip_status=True, include_user_entities=False, cursor=next_cursor)
        if result:
            users.extend(result['users'])
            next_cursor = result['next_cursor']
            return users
        else:
            return users

    def add_to_list(self, users, list_name, batch_size=50):
        # remove users that are already in the list: users - set
        list_members = []
        try:
            list_members = self.get_list_members(list_name)
        except:
            # create a new list
            self.twitter_client.create_list(name=list_name)

        if list_members:
            list_members_names = set([member['screen_name'] for member in list_members])
            users.difference_update(list_members_names)

        # remove bots from candidates
        bots = self.get_list_members(BOT_LIST)
        if bots:
            bots_names = set([bot['screen_name'] for bot in bots])
        users.difference_update(bots_names)

        if users:
            # split users into batches to send to the API
            if len(users) < batch_size:
                batch = users
                self.add_batch_to_list(list_name, batch)

            else:
                for batch in zip(*[iter(list(users))]*batch_size):
                    self.add_batch_to_list(list_name, batch)

            # check that all users were added to the list
            self.get_list_members(list_name)
        else:
            print "No new users added"
        print "\n"


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


def follow_users_from_mongo(db_name, collection_name, lists):
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
    # follow_users_from_mongo(db_name, collection)
    follow_communities_from_mongo(db_name, collection)
    # 3rd TODO check why empty lists are created
    drop_my_empty_lists()


def maintain_my_community_lists(collection=COLLECTION, db_name=DB_NAME):
    collect_new_users(collection, db_name, load_tweets=True)


if __name__ == '__main__':
    maintain_my_community_lists()

