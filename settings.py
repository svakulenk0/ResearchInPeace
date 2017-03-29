#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import time

from pymongo.errors import DuplicateKeyError


APP_KEY = 'PUT YOUR KEY HERE!!!'
APP_SECRET = 'PUT YOUR SECRET HERE!!!'
OAUTH_TOKEN = 'PUT YOUR OAUTH_TOKEN HERE!!!'
OAUTH_TOKEN_SECRET = 'PUT YOUR OAUTH_TOKEN SECRET HERE!!!'

TEST_DBNAME = 'test_twitter'
TEST_COLLECTION = 'test'


# KEYWORDS = ['esc2015', 'eurovision']


def store_tweet(tweet, collection):
    """
    Simple wrapper to facilitate persisting tweets. Right now, the only
    pre-processing accomplished is coercing 'created_at' attribute to datetime.
    """
    if 'created_at' in tweet.keys():
        if not isinstance(tweet['created_at'], datetime.datetime):
            tweet['created_at'] = datetime.datetime.strptime(
                tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
        print tweet['created_at']
        collection.insert(tweet)


def store_tweets(tweets_to_save, collection):
    """
    Simple wrapper to facilitate persisting tweets. Right now, the only
    pre-processing accomplished is coercing 'created_at' attribute to datetime.
    """
    # print tweets_to_save
    for tw in tweets_to_save:
        if not isinstance(tw['created_at'], datetime.datetime):
            tw['created_at'] = datetime.datetime.strptime(
                tw['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
        try:
            collection.insert_one(tw)
            print tw['created_at']
        except DuplicateKeyError as e:
            # print e
            continue
            # TODO update tweet


def handle_rate_limiting(twitter):
    # prepopulating this to make the first 'if' check fail
    app_status = {'remaining': 1}
    while True:
        wait = 0
        if app_status['remaining'] > 0:
            status = twitter.get_application_rate_limit_status(
                resources=['statuses', 'application'])
            app_status = status['resources']['application'][
                '/application/rate_limit_status']
            home_status = status['resources'][
                'statuses']['/statuses/home_timeline']
            if home_status['remaining'] == 0:
                # addding 1 second pad
                wait = max(home_status['reset'] - time.time(), 0) + 1
                time.sleep(wait)
            else:
                return
        else:
            wait = max(app_status['reset'] - time.time(), 0) + 10
            time.sleep(wait)
