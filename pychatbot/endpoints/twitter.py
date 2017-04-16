""" Twitter endpoint for a pychatbot bot, use this to connect your bot to
    Twitter.

    This module needs `tweepy` library.
"""

from __future__ import absolute_import
from threading import Thread
from time import sleep

import twitter


class TwitterEndpoint(object):
    """ Twitter endpoint for a pychatbot bot.

        Example usage:

            >>> ep = TwitterEndpoint(
            ...     consumer_key='consumer_key',
            ...     consumer_secret='consumer_secret',
            ...     access_token='access_token',
            ...     access_token_secret='access_token_secret'
            ... )
            >>> bot.add_endpoint(ep)
            >>> bot.run()

    """

    def __init__(self, consumer_key, consumer_secret,
                 access_token, access_token_secret,):
        self._bot = None
        self._last_processed_dm = 0
        self._polling_should_run = False
        self._polling_is_running = False
        self._polling_frequency = 3

        self._api = twitter.Api(consumer_key=consumer_key,
                                consumer_secret=consumer_secret,
                                access_token_key=access_token,
                                access_token_secret=access_token_secret)

        # ignore all the DMs sent before the start, otherwise the bot will send
        # now the old answers, even the one already answered
        self._calculate_last_processed_dm()

        self._polling_thread = Thread(target=self.polling_new_direct_messages)

    def set_polling_frequency(self, polling_frequency):
        """ Polling frequency setter """
        self._polling_frequency = polling_frequency

    def set_bot(self, bot):
        """ Sets the main bot, the bot must be an instance of
            `pychatbot.bot.Bot`.

            TwitterEndpoint will use the bot to know how to behave.
        """
        self._bot = bot

    def run(self):
        """Starts the polling for new DMs."""

        self._polling_should_run = True
        self._polling_thread.start()

        while not self._polling_is_running:
            sleep(0.5)

    def stop(self):
        """Make the polling for new DMs stop."""

        self._polling_should_run = False
        self._polling_thread.join()

    def polling_new_direct_messages(self):
        """ Strats an infinite loop to see if there are new DMs.

            The loop ends when the `self._polling_should_run` will be false
            (set `True` by `self.run` and `False` by `self.stop`)
        """

        while self._polling_should_run:

            dms = self._api.GetDirectMessages(
                since_id=self._last_processed_dm
            )

            for direct_message in dms:
                self.process_new_direct_message(direct_message)

            # like an heartbeat, to let know that the polling is working
            # useful to `run` to know if the thread is really started
            self._polling_is_running = True

            sleep(self._polling_frequency)

    def process_new_direct_message(self, direct_message):
        """ Method called for each new DMs arrived.
        """

        response = self._bot.process(in_message=direct_message.text)

        self._api.PostDirectMessage(response, user_id=direct_message.sender.id)
        self._last_processed_dm = direct_message.id

    def _calculate_last_processed_dm(self):
        """ Get the last arrived DM. This method should be called just at
            bot startup or the bot can miss some DMs.
        """

        for direct_message in self._api.GetDirectMessages():
            self._last_processed_dm = max(
                self._last_processed_dm,
                direct_message.id
            )
