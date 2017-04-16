""" Unit tests for pychatbot.endpoints.TelegramEndpoint
"""

import json
from time import time, sleep
from twitter.models import DirectMessage

from pychatbot.bot import Bot
from pychatbot.endpoints import TwitterEndpoint


def create_message(text):
    return DirectMessage().NewFromJsonDict(json.loads(
        '{"id": 0, "text": "%s", '
        '"sender": {"id": 0, "screen_name": "greenkey", "name": "greenkey"},'
        '"sender_screen_name": "greenkey"}' % text))


def wait_for(check_callback, polling_time=0.1, timeout=5):
    start = time()
    while time() - start < timeout:
        if check_callback():
            break
        sleep(polling_time)
    else:
        assert False
    assert True


def test_twitter_interface(mocker):
    """ Test that the Twitter API is called when using the endpoint.
    """

    twitterAPI = mocker.patch('twitter.Api')

    class MyBot(Bot):
        "Lowering bot"

        def default_response(self, in_message):
            return in_message.lower()

    bot = MyBot()

    consumer_key = 'consumer_key',
    consumer_secret = 'consumer_secret',
    access_token = 'access_token',
    access_token_secret = 'access_token_secret'

    endpoint = TwitterEndpoint(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
        polling_frequency=0.1
    )
    bot.add_endpoint(endpoint)
    assert endpoint._bot == bot

    bot.run()

    twitterAPI.assert_called_once_with(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token_key=access_token,
        access_token_secret=access_token_secret
    )

    bot.stop()


def test_twitter_default_response(mocker):
    """ Test that the Twitter bot correctly reply with the default response.
    """

    twitterAPI = mocker.patch('twitter.Api')

    class MyBot(Bot):
        "Upp&Down bot"

        last_in_message = ''

        def default_response(self, in_message):
            self.last_in_message = in_message
            return ''.join([
                c.upper() if i % 2 else c.lower()
                for i, c in enumerate(in_message)
            ])

    bot = MyBot()
    endpoint = TwitterEndpoint(
        consumer_key='consumer_key',
        consumer_secret='consumer_secret',
        access_token='access_token',
        access_token_secret='access_token_secret',
        polling_frequency=0.1
    )
    bot.add_endpoint(endpoint)
    bot.run()

    message = create_message("SuperCamelCase")
    twitterAPI().GetDirectMessages.return_value = [message]

    wait_for(lambda: bot.last_in_message == "SuperCamelCase")

    twitterAPI().PostDirectMessage.assert_called_with(
        'sUpErCaMeLcAsE', user_id=message.sender.id
    )

    message = create_message("plain boring text")
    twitterAPI().GetDirectMessages.return_value = [message]

    wait_for(lambda: bot.last_in_message == "plain boring text")

    twitterAPI().PostDirectMessage.assert_called_with(
        'pLaIn bOrInG TeXt', user_id=message.sender.id
    )

    bot.stop()
