#!/usr/bin/env python
# -*- coding: utf-8 -*-

from twython import Twython
from pymongo import MongoClient
# from mongo import connect as Connection

from settings import *
from twitter_settings import *


# spin up twitter api
twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
twitter.verify_credentials()

# spin up database
client = MongoClient()


def exhaustive_search(keyword, db_name=TEST_DBNAME, collection_name=TEST_COLLECTION, verbose=False):
    '''
    keyword <str>
    '''
    print keyword

    db = client[db_name]
    collection = db[collection_name]
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
            store_tweets(statuses, collection)
            # Get the next max_id
        try:
            # Parse the data returned to get max_id to be passed in consequent call.
            next_results_url_params = result['search_metadata']['next_results']
            next_max_id = next_results_url_params.split('max_id=')[1].split(
                '&')[0]
        except:
            # No more next pages
            break


def test_exhaustive_search():
    keyword = "%23ParisAttacks+OR%23paris+OR%23ParisShooting+OR%23prayforparis+OR%23PorteOuverte+OR%23France"
    exhaustive_search(keyword, verbose=True)


if __name__ == '__main__':
    test_exhaustive_search()
