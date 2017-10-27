#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import time

from pymongo.errors import DuplicateKeyError

# Twitter user name
MY_NAME = 'vendiSV'

COLLECTION = 'cs_conferences'
DB_NAME = 'communityTweets'
TEST_DBNAME = 'test_twitter'
TEST_COLLECTION = 'test'

# the lists of hashtags, handles and other keywords for relevant events
CONFERENCE_USERS = [u'@AAAIConference', u'@kdd_news', '@eswc_conf', '@WSDMSocial', '@naacl', '@SIGIRForum', '@NipsConference', '@icmlconf', '@snow_workshop', '@ACMSIGIR', '@ysm_conference', '@ACMRecSys', '@recsyschallenge', '@UMAPconf', '@SemanticsConf', '@ACMHT', '@gamifir', '@nlpandcss', '@clef_initiative', '@fatconference']
CONFERENCE_HASHTAGS = ['#ICLR', '#SIGIR', 'icwsm', '#russir', 'sigmod', '#datasmt', '#ictir', '#jmlr', 'hackzurich']
PAST_CONFERENCES = [u'#LxMLS2014', u'#LxMLS2015', u'#cikm2015', u'#DIR2015', u'#AAAI15', u'#AAAI2015', u'#ICML2015', u'#EMNLP2015', u'#NIPS2015', '#clin24', '#clin26', '#conll2015', '#naacl2015', '#naacl2014', '#lrec2013', '#iswc2015', '#iswc2014', '#iswc2013', '#interspeech2015', '#mediaeval15', '#mediaeval14', '#RANLP2015', '#WASSA2014', '#WASSA2015', '#naacl2013', '#conll2014', '#NLDB2014', '#NLDB2015', '#ecir2014', '#ecir2013', '#sigir2015', '#sigir2014', '#chi2015', '#ecir2015', '#Russir2015', '#russir2012', '#russir2010', '#russir2011', '#russir2013', '#russir2014', '#wsdm2015', u'@WWWfirenze','essir2015', '@airs2015', '#airs2015', '#tacl2015', 'ictir2015']
CONFERENCES_2016 = [u'ICLR2016', u'ICML2016', u'#ecir2016', 'WikiWorkshop2016', u'cikm2016', u'acl2016berlin', u'naacl2016', u'#EMNLP2016', '#lrec2016', 'lrec2016', 'iswc2016', '#mediaeval16', '#WASSA2016', '#NLDB2016', 'sigir2016', 'chi2016', '#CHIIR2016', 'lti16', '#BabelNetLux', 'NeuIR2016', 'CNewsStory16', 'SMnews16', 'icwsm2016', 'websci16', 'eswc2016', 'sumpre2016', 'eamt2016', '#MEPDAW', 'LREC2016SL', 'semdev2016', '#russir2016', '#AAAI16', '#icdm2016', '#IJCAI16', '#ijcai2016', '#ICCSS2016', '#wsdm2016', '#AISTATS2016', '#recsys2016', u'@acl2016', u'@www2016ca', '@icdm2016', '@ijcai16', '#COLING2016', '@ecir2016', '#clef2016', '@emnlp2016', '#acl2016berlin', '#UAI2016', '#semeval2016', 'elag2016', 'ntcir12', 'acmsigmod2016', 'ExploreDB 2016', '#wibih16', 'wibih2016', 'airs2016', '#user2016', 'ictir2016', '@WebScience16', '#umap2016', '#acmht16', '#‎SSSW2016', '#clef2016', '#poltext16', '#SocInfo16', '#MEDIR2016', '#SciPy2016', '#lxmls2016', '#smvw16', '#WiML2016', '@ictir16' '@CIKMIndy2016']
# recent and upcomming events
CONFERENCES_2017 = ['#acl2017nlp', '@acl2017', '#WWW2017', '#essir2017', '#WSDM2017', 'ecir2017', '#acmht17', '#sigir2017', '@SIGIR17', '#ictir2017', '#icmr2017', 'icmr17', 'iclr2017', 'www2017Perth', '#recsys2017', 'SemEval2017', 'CLEF2017', 'ISWC2017', '#AAAI17', '#AAAI2017', 'eswc2017', 'IJCAI17', 'eacl2017', 'ICWE2017', 'vldb2017', 'hackzurich2017', 'IJCAI2017', '#nips2017']
CONFERENCES_2018 = ['@www2018', '#LREC2018', 'iswc2018']

# keywords to collect tweets, e.g. ['esc2015', 'eurovision']
KEYWORDS = CONFERENCE_USERS + CONFERENCES_2017 + CONFERENCES_2018 + CONFERENCE_HASHTAGS

# Twitter lists
# MY_LISTS = ['iclr2017', 'coling2016', 'icdm2016', 'sigir2016', 'naacl2016', 'websci16', 'LREC2016', 'DeepLearning', 'icml2016', 'MachineLearning', 'NLProc', 'acl2016berlin', 'cikm2016', 'ictir2016', 'recsys2016', 'iswc2016', 'WSDM2017', 'nips2016', 'kdd2016', 'jmlr', 'emnlp2016', 'www2017Perth']
BOT_LIST = 'Filter'
# sample list (one of my existing Twitter lists) for testing purposes
MY_LIST = 'naacl2016'

# topic hierarchy of events: individual event series and research areas
COMMUNITIES = {'VLDB': ['vldb2017'],
               'ICWE': ['ICWE2017'],
               'ICLR': ['iclr2016', 'iclr2017', 'iclr'],
               'ECIR': ['ecir2017', 'ecir2016'],
               'EACL': ['eacl2017'],
               'ISWC' : ['iswc2017'],
               'AI': ['#AAAI17', '#AAAI2017', 'IJCAI2017'],
               'NLP': ['naacl2016', 'acl2016berlin', 'emnlp2016', 'LREC2016', 'eacl2017', '#acl2017nlp', '@acl2017'],
               'InformationRetrieval': ['sigir2016', 'recsys2016', 'ictir2016', 'sigir2017'],
               'SemanticWeb': ['iswc2016'],
               'WebScience': ['websci16', 'WSDM2017', 'kdd2016', 'cikm2016', 'www2017Perth', 'WWW2017', 'ICWE2017'],
               'HackZurich': ['hackzurich2017', 'hackzurich'],
               'MachineLearningResearch': ['nips2016', '#nips2017', 'jmlr', 'icml2016', 'WiML2016', 'iclr2016', 'iclr2017', 'iclr']}


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
