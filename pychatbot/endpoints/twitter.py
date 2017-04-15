""" Twitter endpoint for a pychatbot bot, use this to connect your bot to
    Twitter.

    This module needs `tweepy` library.
"""

from __future__ import absolute_import
from threading import Thread
from time import sleep

import twitter


class TwitterEndpoint(object):

    def __init__(self, consumer_key, consumer_secret,
                 access_token, access_token_secret):
        self._api = twitter.Api(consumer_key=consumer_key,
                                consumer_secret=consumer_secret,
                                access_token_key=access_token,
                                access_token_secret=access_token_secret)
        self._polling_thread = Thread(target=self.polling_new_direct_messages)
        self.calculate_last_processed_dm()
        self._polling_is_running = False

    def set_bot(self, bot):
        self._bot = bot

    def run(self):
        self._pollint_running = False
        self._polling_thread.start()

        while not self._polling_is_running:
            sleep(0.5)

    def stop(self):
        self._polling_should_run = False

    def polling_new_direct_messages(self):
        self._polling_should_run = True

        while self._polling_should_run:
            dms = self._api.GetDirectMessages(
                since_id=self._last_processed_dm
            )
            for direct_message in dms:
                self.process_new_direct_message(direct_message)
            self._polling_is_running = True
            sleep(5)

    def process_new_direct_message(self, direct_message):
        response = self._bot.process(in_message=direct_message.text)

        self._api.PostDirectMessage(response, user_id=direct_message.sender.id)
        self._last_processed_dm = direct_message.id

    def calculate_last_processed_dm(self):
        self._last_processed_dm = 0
        for direct_message in self._api.GetDirectMessages():
            self._last_processed_dm = max(
                self._last_processed_dm,
                direct_message.id
            )
