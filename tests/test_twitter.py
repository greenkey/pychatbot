''' Unit tests for pychatbot.endpoints.TelegramEndpoint
'''

import pytest
from time import time, sleep
from twitter.models import DirectMessage

from pychatbot.bot import Bot
from pychatbot.endpoints import TwitterEndpoint


class DirectMessageMocker:
    def __init__(self):
        self.direct_messages_sent = []

    def add_direct_message(self, text):
        new_dm = DirectMessage().NewFromJsonDict({
            'id': len(self.direct_messages_sent) + 1,
            'text': text,
            'sender': {
                'id': 0,
                'screen_name': 'greenkey',
                'name': 'greenkey'
            },
            'sender_screen_name': 'greenkey'
        })
        self.direct_messages_sent.append(new_dm)

        return new_dm

    def get_message_list(self, since_id=-1):
        return [dm for dm in self.direct_messages_sent if dm.id > since_id]


@pytest.fixture()
def direct_messages():
    return DirectMessageMocker()


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
    ''' Test that the Twitter API is called when using the endpoint.
    '''

    twitterAPI = mocker.patch('twitter.Api')

    class MyBot(Bot):
        'Lowering bot'

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
        access_token_secret='access_token_secret'
    )
    endpoint.set_polling_frequency(0.1)
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


def test_twitter_default_response(mocker, direct_messages):
    ''' Test that the Twitter bot correctly reply with the default response.
    '''

    twitterAPI = mocker.patch('twitter.Api')
    twitterAPI().GetDirectMessages = direct_messages.get_message_list

    class MyBot(Bot):
        'Upp&Down bot'

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
        access_token_secret='access_token_secret'
    )
    endpoint.set_polling_frequency(0.1)
    bot.add_endpoint(endpoint)
    bot.run()

    message = direct_messages.add_direct_message('SuperCamelCase')
    wait_for(lambda: bot.last_in_message == 'SuperCamelCase')
    twitterAPI().PostDirectMessage.assert_called_with(
        'sUpErCaMeLcAsE', user_id=message.sender.id
    )

    message = direct_messages.add_direct_message('plain boring text')
    wait_for(lambda: bot.last_in_message == 'plain boring text')
    twitterAPI().PostDirectMessage.assert_called_with(
        'pLaIn bOrInG TeXt', user_id=message.sender.id
    )

    bot.stop()


def test_dont_process_old_dms(mocker, direct_messages):
    ''' Test that the Twitter bot ignore the DMs sent before its start.
    '''

    twitterAPI = mocker.patch('twitter.Api')
    twitterAPI().GetDirectMessages = direct_messages.get_message_list
    message = direct_messages.add_direct_message('previous message')

    class MyBot(Bot):
        'Echo bot'

        last_in_message = ''

        def default_response(self, in_message):
            self.last_in_message = in_message
            return in_message

    bot = MyBot()
    endpoint = TwitterEndpoint(
        consumer_key='consumer_key',
        consumer_secret='consumer_secret',
        access_token='access_token',
        access_token_secret='access_token_secret'
    )
    endpoint.set_polling_frequency(0.1)
    bot.add_endpoint(endpoint)
    bot.run()

    message = direct_messages.add_direct_message('this is the first message')
    wait_for(lambda: bot.last_in_message == 'this is the first message')
    twitterAPI().PostDirectMessage.assert_called_once_with(
        'this is the first message', user_id=message.sender.id
    )

    message = direct_messages.add_direct_message('this is the last message')
    wait_for(lambda: bot.last_in_message == 'this is the last message')
    assert twitterAPI().PostDirectMessage.call_count == 2
    twitterAPI().PostDirectMessage.assert_called_with(
        'this is the last message', user_id=message.sender.id
    )

    bot.stop()
