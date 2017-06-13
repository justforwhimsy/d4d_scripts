#!/usr/bin/python

import tweepy
import json

consumer_key = 'KEY'
consumer_secret = 'SECRET'
access_token = 'TOKEN'
access_token_secret = 'TOKEN SECRET'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

public_tweets = api.home_timeline()

results = api.search_users('Clark County')
print(results)
for items in results:
    pages = items['data']
    for page in pages:
        page_id = page['id']
        fb_page = get_page(page_id)
        # print(fb_page)
        #TODO Get the state for the page and verify it matches the county we are looking for.
        # print(fb_page)
        try:
            page_state = fb_page['location']['state']
            states[page_state].append(page_id)
        except Exception as e:
            print("Failed to find state for " + fb_page['name'])
            print(e)
    #
# for tweet in public_tweets:
#     print(tweet.text)
# url = ''
# user = api.get_user('barackobama')
# followers = user.followers()
# print(user.followers_count)
# print(len(followers))
# count = 1
# for follower in tweepy.Cursor(api.followers, user='anactofwhimsy').items():
#     print(follower.screen_name)
#     count += 1
#
# print(count)
# Todo: find API call that will collect all related twitter accounts.
# Crawl through accounts to a certain limit
