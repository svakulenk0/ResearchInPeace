#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on Dec 21, 2016

.. codeauthor: svitlana vakulenko
    <svitlana.vakulenko@gmail.com>

Collect related users by a set of seed users

'''

from create_community_list import Twitter_Processor


def test_retrieve_my_friends(limit=5):
    TP = Twitter_Processor()
    users = TP.retrieve_friends_of(limit=limit)
    assert len(users) == limit


def expand_list_with_fofs(list_name=None):
    keyword = 'wien'
    # print [user['screen_name'] for user in users if keyword in user['location'].split()]
    # print [user['screen_name'] for user in users if keyword in user['description']]


def move_my_friends_to_list(list_name='wien'):
    TP = Twitter_Processor()
    users = TP.retrieve_friends_of()
    if users:
        user_names = [user['screen_name'] for user in users]
        TP.add_to_list(set(user_names), list_name)
        TP.unfriend(user_names)
        move_my_friends_to_list(list_name=list_name)


if __name__ == '__main__':
    move_my_friends_to_list()
