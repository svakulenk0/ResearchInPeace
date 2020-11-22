#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on Nov 22, 2020

.. codeauthor: svitlana vakulenko
    <svitlana.vakulenko@gmail.com>

Step 1. Start out with a set of seed keywords, e.g. hashtags for CS conferences.
Step 2. Add all users who tweeted using these hashtags to a public Twitter list.

'''

from twython import Twython

from settings import *
from twitter_settings import *


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

    def delete_list_members(self, list_name, members):
        self.twitter_client.delete_list_members(slug=list_name,
                                                owner_screen_name=MY_NAME,
                                                screen_name=members)

    def retrieve_my_lists(self):
        return self.twitter_client.show_lists(screen_name=MY_NAME)

    def add_batch_to_list(self, list_id, batch):
        # concatenate user screen names for the query
        users_string = ",".join(batch)
        try:
            # users_string = 'SRajdev'
            print('Adding users', list_id, MY_NAME, users_string)

            self.twitter_client.create_list_members(list_id=list_id, screen_name=users_string)
            print "Added " + str(len(batch)) + " new users"
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

    def add_to_list(self, users, list_id, batch_size=50, deduplicate=True):
        '''
        users <set>
        '''
        # remove users that are already in the list: users - set

        # if deduplicate:
        #     print('deduplicating')
        #     list_members = []
        #     # try:
        #     list_members = self.get_list_members(list_id=list_id)
        #     # except:
        #     #     # create a new list
        #     #     self.twitter_client.create_list(name=list_name)

        #     if list_members:
        #         list_members_names = set([member['screen_name'] for member in list_members])
        #         users.difference_update(list_members_names)

        # remove bots from candidates
        bots = self.get_list_members(BOT_LIST)
        if bots:
            bots_names = set([bot['screen_name'] for bot in bots])
        users.difference_update(bots_names)

        if users:
            # split users into batches to send to the API
            if len(users) < batch_size:
                batch = users
                self.add_batch_to_list(list_id, batch)

            else:
                for batch in zip(*[iter(list(users))]*batch_size):
                    self.add_batch_to_list(list_id, batch)

            # check that all users were added to the list
            # self.get_list_members(list_name)
        else:
            print "No new users added"
        print "\n"


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


def follow_users_by_hashtags(keyword, verbose=True):

    drop_my_empty_lists()

    print keyword

    # spin up twitter api
    twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    twitter.verify_credentials()
    TP = Twitter_Processor()

    # list_id = TP.twitter_client.create_list(name=keyword)['id']
    list_id = 1330585430845251584
    print list_id

    time.sleep(1) # Sleep one second


    next_max_id = None
    while True:
        # params = {'q': 'eurovision', 'count': 100, 'max_id': next_max_id}
        params = {'q': keyword + " -filter:retweets", 'count': 100, 'max_id': next_max_id}
        # handle_rate_limiting(twitter)
        result = twitter.search(**params)
        statuses = result['statuses']
        if statuses:
            if verbose:
                print len(statuses), 'tweets retrieved'
            # Get the next max_id

        users = list(set([s['user']['screen_name'] for s in statuses]))
        # print users
        # break
        print "Found " + str(len(users)) + " users in " + keyword
        try:
            TP.add_to_list(set(users), list_id)
        except Exception as e:
            print e
            pass

        try:
            # Parse the data returned to get max_id to be passed in consequent call.
            next_results_url_params = result['search_metadata']['next_results']
            next_max_id = next_results_url_params.split('max_id=')[1].split(
                '&')[0]
        except:
            # No more next pages
            break


if __name__ == '__main__':
    follow_users_by_hashtags('#emnlp2020')
