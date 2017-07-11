#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on Dec 27, 2016

.. codeauthor: svitlana vakulenko
    <svitlana.vakulenko@gmail.com>

Collect users with a specified location in the description

'''

import numpy as np
import time

from create_community_list import Twitter_Processor
from twython.exceptions import TwythonRateLimitError

# from crawl_friends import expand_list_with_fofs

KYIV_KEYWORDS = ['kyiv', 'київ', 'киев']
WIEN_KEYWORDS = ['wien', 'vienna']
MOSCOW_KEYWORDS = ['moscow', 'москва']
NYC_KEYWORDS = ['New York City']
AMSTERDAM_KEYWORDS = ['amsterdam']
LISTS = ['kyiv', 'wien', 'moscow', 'Nyc', 'amsterdam']

LOCAL_COMMUNITIES = {
    'kyiv': ['kyiv', 'київ', 'киев'],
    'wien': ['wien', 'vienna'],
    'moscow': ['moscow', 'москва'],
    'Nyc': ['New York City'],
    'amsterdam': ['amsterdam'],
}


def get_users_by_location(locations, keyword, list):
    TP = Twitter_Processor()
    TP.collect_members_based_on_location(locations, keyword, list_name=list)


def expand_list_with_friends(location):
    list_name = location
    keywords = LOCAL_COMMUNITIES[list_name]
    TP = Twitter_Processor()
    members = TP.get_list_members(list_name)
    # shuffle the list of users randomly
    for member in np.random.permutation(members):
        print "User:", member['screen_name']
        # get friends
        friends = TP.retrieve_friends_of(member['screen_name'], 200)
        print "#Friends:", len(friends)
        # check user-specified location
        users = [user['screen_name'] for keyword in keywords
               for user in friends for location in user['location'].split() if keyword in location.lower().encode('utf-8')]
        print "#Friends in " + list_name +":", len(users)
        TP.add_to_list(set(users), list_name)


def test_expand_list_with_friends():
    expand_list_with_friends(location='amsterdam')


def test_get_users_by_location():
    get_users_by_location(KYIV_KEYWORDS, KYIV_KEYWORDS[0], LISTS[0])
    get_users_by_location(MOSCOW_KEYWORDS, MOSCOW_KEYWORDS[0], LISTS[2])
    get_users_by_location(WIEN_KEYWORDS, WIEN_KEYWORDS[0], LISTS[1])
    get_users_by_location(NYC_KEYWORDS, NYC_KEYWORDS[0], LISTS[3])


if __name__ == '__main__':
    # test_get_users_by_location()
    while True:
        try:
            expand_list_with_friends(location='amsterdam')
        except TwythonRateLimitError as e:
            print "TwythonRateLimitError... Waiting for 2000 seconds"
            time.sleep(2000)
