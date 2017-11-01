#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Methods to issue various requests to the Twitter API

TODO
* cache results
maintain cache of lates call to Twitter and results to reduce computation time
* aggregate several hashtags lists into communities
* !!! make overall summary across all communities !!!
* implement bot detector filter! or off-topics
'''

from collections import Counter

from twython import Twython

import urllib2
from bs4 import BeautifulSoup

from twitter_settings import *
# from topic_model import model_topics_lda

import time

from flask import Markup

MY_LISTS = ['sigir2016', 'naacl2016', 'websci16', 'LREC2016', 'DeepLearning', 'icml2016', 'NLProc', 'acl2016berlin', 'cikm2016', 'ictir2016', 'recsys2016', 'iswc2016', 'WSDM2017', 'nips2016', 'kdd2016', 'jmlr', 'emnlp2016', 'Cs']
TEST_LISTS = ['websci16', 'naacl2016']


def get_hashtags(list_name):
    twitter_client = Twython(APP_KEY, APP_SECRET,
                             OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    next_max_id = None
    while True:
        # contains retweets!
        params = {'slug': list_name, 'owner_screen_name': MY_NAME,
                  'count': 1000000, 'max_id': next_max_id}
        statuses = twitter_client.get_list_statuses(**params)

        if statuses:
            # generate links to twitter hashtags
            hashtag_list = ["<a href='https://twitter.com/search?q=%23" +
                            hashtag['text'] + "'>#" + hashtag['text'] + "</a>"
                            for tweet in statuses
                            for hashtag in tweet['entities']['hashtags']]
            hashtags = ''.join(hashtag_list)
            # print(hashtags)
            # yield Markup(hashtags)
            return hashtags
            # TODO whats here about the loop???
            next_max_id = statuses[-1]['id']
        else:
            next_max_id = None


def find_most_popular_tweets(tweets):
    '''
    + find most popular urls in the same loop
    '''
    # by retweet_count
    popular_tweets = Counter()
    popular_urls = Counter()
    popular_media = Counter()
    original_tweets = {}
    for tweet in tweets:
        # filter out retweets
        if 'retweeted_status' not in tweet.keys():
            # ranking score formula retweets+favorites
            score = tweet['retweet_count'] + tweet['favorite_count']
            popular_tweets[tweet['id_str']] = score

            # rank urls
            urls = [url_object['expanded_url'] for url_object in tweet['entities']['urls']
                if url_object['expanded_url'].split('/')[2] != 'twitter.com']
            for url in urls:
                popular_urls[url] = score
            # rank media urls
            if 'media' in tweet['entities']:
                media = [media_object['media_url'] for media_object in tweet['entities']['media']]
                for url in media:
                    popular_media[url] = score
            # original_tweets[tweet['id_str']] = (tweet['text'], tweet['created_at'])
            original_tweets[tweet['id_str']] = (tweet['text'], tweet['created_at'][11:19], tweet['user']['name'])
    return (popular_tweets, original_tweets, popular_urls, popular_media)


# TODO embed selected tweets in templates timeline-like interface ordered

def get_main_stream_sample():
    """
    Detect main stream news for today
    """
    pass

def get_worldwide_trends(twitter_client):
    response = twitter_client.get_place_trends(id=1)
    for trend in response[0]['trends']:
        print trend['name']


def get_timeline_for_lists(lists=MY_LISTS, n=5):
    twitter_client = Twython(APP_KEY, APP_SECRET,
                             OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    top_tweet_ids = []
    for list_name in lists:
        print list_name
        all_tweets = twitter_client.get_list_statuses(slug=list_name,
                                              owner_screen_name=MY_NAME,
                                              count=1000000)
        # Filter: only the tweets 1)posted today, 2)in English or undefined language
        today = time.strftime("%a %b %d")
        recent_tweets = [tweet for tweet in all_tweets if tweet['created_at'][:10] == today if tweet['lang'] in ('en','und')] 
        tweets = recent_tweets
        # TODO simplify the function
        popular_tweets, original_tweets, popular_urls = find_most_popular_tweets(tweets)
        top_ranking = Counter(popular_tweets).most_common(n)
        top_tweet_ids.extend([tweet for tweet,count in top_ranking])
    # print set(top_tweet_ids)

    top_tweets = []
    for tweet_id in set(top_tweet_ids):
        #     print tweet
                # TODO produce tweet embeddings
                # tweet_id = tweet[0]
                # return: tweet_id, tweet_text, tweet_created_at, rank=retweets+likes
                # top_tweets.append((tweet_id, original_tweets[tweet_id][0],
                                   # original_tweets[tweet_id][1], tweet[1]))
        tweet = twitter_client.get_oembed_tweet(url="https://twitter.com/Interior/status/"+tweet_id, maxwidth=550, align='center')
        top_tweets.append(Markup(tweet['html']))
    print len(top_tweets)
    return top_tweets


def aggregate_stats(all_tweets, request, n=5, n_tweets=50, popular_tweets=True, retrive_urls=True, count_languages=False):
    # returns up to 200 most recent tweets per call
    # print len(all_tweets)
    # count=1000000 1M tweets is the upper limit of the API
    # Filter: only the tweets 1)posted today, 2)in English or undefined language
    
    # today = time.strftime("%a %b %d")
    # print today
    # print request
    # recent_tweets = [tweet for tweet in all_tweets if tweet['created_at'][:10] == today if tweet['lang'] in ('en','und')] 
    # tweets = recent_tweets
    
    # no pre-filtering applied
    tweets = all_tweets

    # calculate number of tweets published within the last hour
    # now = time.strftime("%Y-%m-%d")
    # datetime.datetime.now() - datetime.timedelta(minutes=15)
    # recent_tweets = [tweet for tweet in all_tweets if tweet['created_at'][:10] == today if tweet['lang'] in ('en','und')] 


    last_tweet_hour = int(tweets[0]['created_at'][11:13])
    first_tweet_hour = int(tweets[-1]['created_at'][11:13])
    n_tweets = len(tweets)
    # tweets/hour
    stream_velocity = n_tweets/(last_tweet_hour - first_tweet_hour + 1)


    # print stream_velocity
    # Analytics: topics, hashtags, users, tweets, urls
    # model_topics_lda(tweets)
    # model_topics_lda(corpus, dictionary)
    # model_topics(tweets)
    users = [tweet['user']['screen_name'] for tweet in tweets]
    languages = []
    if count_languages:
        languages = [tweet['metadata']['iso_language_code'] for tweet in tweets]
    hashtags = [hashtag['text'] for tweet in tweets for hashtag in
                tweet['entities']['hashtags']]

    # print "Top urls distributed within the community:"
    # filter out urls to tweets
    # takes too much time!
    # url_titles = None
    urls = []
    if retrive_urls:
        urls = [url_object['expanded_url'] for tweet in tweets
                for url_object in tweet['entities']['urls']
                if url_object['expanded_url'].split('/')[2] != 'twitter.com']
        # print urls
        for tweet in tweets: 
            if 'media' in tweet['entities']:
                media = [media_object['media_url'] for media_object in tweet['entities']['media']]
                urls.extend(media)

        # TODO retrieve top tweets by retweets/likes
        # TODO filter out Twitter urls
        # url_titles = fetch_page_titles(urls)
    # TODO add sample tweets mentioning urls
    # TODO most popular urls by number of likes/retweets?

    mentions = [user['screen_name'] for tweet in tweets for user in
                tweet['entities']['user_mentions']]
    # 'urls': url_titles 'date': today,  'urls': Counter(urls).most_common(n)
    stats = {'list': request, 'languages': Counter(languages).most_common(n),
             'users': Counter(users).most_common(n),
             'hashtags': Counter(hashtags).most_common(n),
             'mentions': Counter(mentions).most_common(n),
             'velocity': stream_velocity}

    if popular_tweets:
        popular_tweets, original_tweets, popular_urls, popular_media = find_most_popular_tweets(tweets)
        top_ranking = Counter(popular_tweets).most_common(n_tweets)
        top_tweets = []
        for tweet in top_ranking:
            # TODO produce tweet embeddings
            tweet_id = tweet[0]
            # return: tweet_id, tweet_text, tweet_created_at, rank=retweets+likes
            rank = tweet[1]
            if rank > 0:
                top_tweets.append((tweet_id, original_tweets[tweet_id][0],
                               original_tweets[tweet_id][1], rank, original_tweets[tweet_id][2]))
            # response = twitter_client.get_oembed_tweet(url="https://twitter.com/Interior/status/"+tweet[0], maxwidth=550, align='center')
            # top_tweets.append(Markup(response['html']))
        stats['top_tweets'] = top_tweets
        stats['urls'] = popular_urls.most_common(n)
        stats['media'] = popular_media.most_common(n)

    return stats


def print_list_stats(stats_list):
    for stats in stats_list:
        print "List: ", stats['list']

        print "Active users:"
        print Counter(stats['users']).most_common(5)

        print "Trending hashtags:"
        # print "Top hashtags used in the community:"
        print Counter(stats['hashtags']).most_common(5)

        print "Trending urls:"
        # print "Top urls distributed within the community:"
        # print Counter(stats['urls']).most_common(5)
        print stats['urls']

        print "Trending users (mentions):"
        top_mentions = [user[0] for user in
                        Counter(stats['mentions']).most_common(5)]
        print top_mentions

        print "Trending tweets:"
        print stats['top_tweets']


def fetch_page_titles(urls, n=5):
    top_urls = [url for url in Counter(urls).most_common(n)]
    top_titles = []
    for url, url_count in top_urls:
        # if url_count < 2:
        #     return top_titles
        try:
            response = urllib2.urlopen(url)
        except urllib2.HTTPError:
            continue
        except urllib2.URLError, e:
            print e.args
            continue
        html = response.read()
        soup = BeautifulSoup(html, "html.parser")
        # TODO check other options for more descriptive title, header title of the article
        title = soup.title
        if title:
            top_titles.append((url, title.string, url_count))
    return top_titles

# def render_list_stats(stats_list, n=5):
#     stats_string = []
#     for stats in stats_list:
#         # stats_string.append "List: " + stats['list']

#         stats_string += "Active users:"
#         # stats_string += Counter(stats['users']).most_common(5)
#         # The Top-N
#         # print("The Top {0} words".format(n))
#         for word, count in Counter(stats['users']).most_common(n):
#             stats_string += "{0}: {1}".format(word, count)

#         # stats_string += "Trending hashtags:"
#         # # print "Top hashtags used in the community:"
#         # stats_string += Counter(stats['hashtags']).most_common(n)

#         # stats_string += "Trending urls:"
#         # # print "Top urls distributed within the community:"
#         # stats_string += Counter(stats['urls']).most_common(n)

#         # stats_string += "Trending users (mentions):"
#         # top_mentions = [user[0] for user in
#         #                 Counter(stats['mentions']).most_common(n)]
#         # stats_string += top_mentions
#     return stats_string


def get_list_tweets(twitter_client, list_name):
    return twitter_client.get_list_statuses(slug=list_name,
                                            owner_screen_name=MY_NAME,
                                            count=1000000)

def get_hashtag_tweets(twitter_client, hashtag, only_english=False):
    '''
    Twitter API since date mask: “2015-12-21” (year-month-day)
    Filter out only the original tweets excluding replies and retweets
    Return only English tweets posted today
    '''
    today = time.strftime("%Y-%m-%d")
    # print today
    request = '#' + hashtag + " -filter:retweets AND -filter:replies since:" + today
    if only_english:
        return twitter_client.search(q=request, result_type='recent', include_entities='true',
                                     count=100, lang='en')['statuses']
    else:
        return twitter_client.search(q=request, result_type='recent', include_entities='true',
                                     count=100)['statuses']

# def get_stats_for_lists(lists=MY_LISTS):
def get_stats(requests=MY_LISTS, get_tweets_function=get_list_tweets, count_languages=False):
    twitter_client = Twython(APP_KEY, APP_SECRET,
                             OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    stats_list = []
    for request in requests:
        tweets = get_tweets_function(twitter_client, request)
        # print tweets
        stats_list.append(aggregate_stats(tweets, request, count_languages=count_languages))
    # print_list_stats(stats_list)
    return stats_list
    # return render_list_stats(stats_list)


def retrieve_my_lists():
    twitter_client = Twython(APP_KEY, APP_SECRET,
                             OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    lists = twitter_client.show_lists(screen_name=MY_NAME)
    lists = [(twitter_list['slug'], twitter_list['member_count']) for twitter_list in lists]
    lists.sort(key=lambda tup: tup[1], reverse=True)
    print lists
    return lists

def test_list_stats(lists=TEST_LISTS):
    '''Test list stats'''
    stats_list = get_stats_for_lists(lists)
    # print_list_stats(stats_list)

def find_topics(list_name, twitter_client, mainstream_topics=None, print_documents=False):
    all_tweets = twitter_client.get_list_statuses(slug=list_name,
                                              owner_screen_name=MY_NAME,
                                              count=1000000)
    print len(all_tweets)
    return model_topics_lda(all_tweets, mainstream_topics, print_documents)

def test_twitter_trends():
    twitter_client = Twython(APP_KEY, APP_SECRET,
                             OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    get_worldwide_trends(twitter_client)

def find_trending_topics(topic_lists, mainstream_lists):
    twitter_client = Twython(APP_KEY, APP_SECRET,
                             OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    mainstream_topics = set()
    for mainstream_list in mainstream_lists:
        mainstream_topics.update(find_topics(mainstream_list, twitter_client))
    print mainstream_topics
    for topic_list in topic_lists:
        print topic_list
        find_topics(topic_list, twitter_client, mainstream_topics, print_documents=True)
        

def test_find_trending_topics():
    find_trending_topics(TEST_LISTS, ['wien', 'Nyc'])    

def test_get_timeline_for_lists():
    get_timeline_for_lists()

if __name__ == "__main__":
    test_get_timeline_for_lists()
    # test_list_stats()
    # test_find_trending_topics()
    # test_twitter_trends()

