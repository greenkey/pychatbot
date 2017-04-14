""" Twitter endpoint for a pychatbot bot, use this to connect your bot to
    Twitter.

    This module needs `tweepy` library.
"""

from __future__ import absolute_import
import tweepy


class TwitterEndpoint(object):

    def __init__(self, consumer_key, consumer_secret,
                 access_token, access_token_secret):
        self._auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        self._auth.set_access_token(access_token, access_token_secret)
        self._api = tweepy.API(self._auth)

    def set_bot(self, bot):
        self._bot = bot

    def run(self):
        pass

    def stop(self):
        pass
