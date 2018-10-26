# ResearchInPeace (R.I.P.)
Breaking News Detector for Academics.

Academic News Engine over the Twitter stream with an alternative interface to Twitter API listing a set of topics to retrieve the most recent tweets for on demand. [Demo](https://svakulenko.ai.wu.ac.at/lists/)

It does not use any classifiers atm the tweets are retrieved by the hashtag or from the users in [my Twitter lists](https://twitter.com/svakulenk0/lists)

The user lists are compiled automatically based on a relevant keyword/hashtag (see create_community_list.py script).


## Dependencies

* twython
* pymongo

## Run

python create_community_list.py -- to load recent tweets in batch