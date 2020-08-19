import datetime
import logging
import tweepy
import os
import time
from time import sleep
import random

from tweepy import api

maxTweets = 3200

accName = None
APIKey = None
APIKeySecret = None
AccessToken = None
AccessTokenSecret = None

# Authenticate to Twitter
auth = tweepy.OAuthHandler(APIKey, APIKeySecret)
auth.set_access_token(AccessToken, AccessTokenSecret)

# Create API object
api = tweepy.API(auth, wait_on_rate_limit=True,
    wait_on_rate_limit_notify=True)

def main():

    logging.info("Processing 1st acc...")
    process(accName, APIKey, APIKeySecret, AccessToken, AccessTokenSecret, "#writingcommunity")

    logging.info("Processed 1st acc")

def process(name, key, keysecret, token, tokensecret, tag):

    # Authenticate to Twitter
    auth = tweepy.OAuthHandler(key, keysecret)
    auth.set_access_token(token, tokensecret)

    # Create API object
    api = tweepy.API(auth, wait_on_rate_limit=True,
        wait_on_rate_limit_notify=True)

    searchTweets(api, tag)


def searchTweets(api, tag):

    sleep(10)

    logging.info("Searching by tag: " + tag)
    tweetsIterator = tweepy.Cursor(api.search, q=tag, lang="en").items(500)

    tweets = list(tweetsIterator)

    tweets.sort(key=lambda x: x.favorite_count, reverse=True)

    del tweets[250:len(tweets)]

    retweetLikeGivenTweets(api, tweets)

def retweetLikeGivenTweets(api, tweets):
    
    randIndex = random.randrange(0, 200)

    logging.info(len(tweets))

    tweet = tweets[randIndex]

    favorited = api.get_status(tweet.id).favorited

    if favorited:
        logging.info("Tweet already favorited, entering recursion....")
        retweetLikeGivenTweets(api, tweets)

    else:
        api.create_favorite(tweets[randIndex].id)
        logging.info("Tweet favorited")

        sleep(30)

        logging.info("Attempting to retweet tweet...")
        api.retweet(tweets[randIndex].id)
        logging.info("Retweeted by tag successful")


# Retweets a tweet from target account
def retweetTarget(accName, api):

    alltweets =[]

    newtweets = api.user_timeline(screen_name = accName, count=200, result_type='popular')

    alltweets.extend(newtweets)

    oldest = alltweets[-1].id - 1

    #keep grabbing tweets until there are no tweets left to grab
    while len(newtweets) > 0:
        
        #all subsiquent requests use the max_id param to prevent duplicates
        new_tweets = api.user_timeline(screen_name = accName,count=200,max_id=oldest)
        
        #save most recent tweets
        alltweets.extend(new_tweets)
        
        #update the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1

        if(len(alltweets) >= maxTweets):
            break

    alltweets.sort(key=lambda x: x.favorite_count, reverse=True)

    del alltweets[250:len(alltweets)]

    tweet = random.choice(alltweets)

    api.retweet(tweet.id)

if __name__ == '__main__':
    main()