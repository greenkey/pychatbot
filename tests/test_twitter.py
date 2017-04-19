''' Unit tests for pychatbot.endpoints.TelegramEndpoint
'''

import pytest
import json
from tweepy.models import DirectMessage, User

from .conftest import wait_for

from pychatbot.bot import Bot, command
from pychatbot.endpoints import TwitterEndpoint


class DirectMessageMocker:
    """ Fixture to create fake DirectMessages
    """

    def __init__(self):
        self.direct_messages_sent = []

    def add_direct_message(self, text):
        """ Create a fake DirectMessage and adds it to `self.direct_messages`
        """

        new_dm = DirectMessage().parse(api=None, json={
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
        """ Retrieve the list of DMs created with `add_direct_message`.
            Use this as patch for the function retrieving DMs.
        """

        return [dm for dm in self.direct_messages_sent if dm.id > since_id]


@pytest.fixture()
def direct_messages():
    """ Fixture: returns `DirectMessageMocker`, all the logic is in the class
        definition.
    """
    return DirectMessageMocker()


def create_fake_user():
    new_user = User.NewFromJsonDict({
        'id': 0,
        'name': 'greenkey',
        'screen_name': 'greenkey',
        'following': False
    })
    return new_user


def test_twitter_interface(mocker, create_bot):
    ''' Test that the Twitter API is called when using the endpoint.
    '''

    mOAuthHandler = mocker.patch('tweepy.OAuthHandler')
    mAPI = mocker.patch('tweepy.API')

    class MyBot(Bot):
        'Lowering bot'

        def default_response(self, in_message):
            return in_message.lower()

    consumer_key = 'consumer_key',
    consumer_secret = 'consumer_secret',
    access_token = 'access_token',
    access_token_secret = 'access_token_secret'

    tep = TwitterEndpoint(
        consumer_key=consumer_key, consumer_secret=consumer_secret,
        access_token=access_token, access_token_secret=access_token_secret
    )
    tep.set_polling_frequency(0.1)
    bot = create_bot(MyBot(), tep)

    assert bot.endpoints[0]._bot == bot

    mOAuthHandler.assert_called_once_with(consumer_key, consumer_secret)
    mOAuthHandler().set_access_token.assert_called_once_with(
        access_token, access_token_secret
    )
    mAPI.assert_called_once_with(mOAuthHandler())


def test_twitter_default_response(mocker, direct_messages, create_bot):
    ''' Test that the Twitter bot correctly reply with the default response.
    '''

    mAPI = mocker.patch('tweepy.API')
    mAPI().direct_messages = direct_messages.get_message_list

    class MyBot(Bot):
        'Upp&Down bot'

        last_in_message = ''

        def default_response(self, in_message):
            self.last_in_message = in_message
            return ''.join([
                c.upper() if i % 2 else c.lower()
                for i, c in enumerate(in_message)
            ])

    tep = TwitterEndpoint(
        consumer_key='', consumer_secret='',
        access_token='', access_token_secret=''
    )
    tep.set_polling_frequency(0.1)
    bot = create_bot(MyBot(), tep)

    message = direct_messages.add_direct_message('SuperCamelCase')
    wait_for(lambda: bot.last_in_message == 'SuperCamelCase')
    mAPI().send_direct_message.assert_called_with(
        'sUpErCaMeLcAsE', user_id=message.sender.id
    )

    message = direct_messages.add_direct_message('plain boring text')
    wait_for(lambda: bot.last_in_message == 'plain boring text')
    mAPI().send_direct_message.assert_called_with(
        'pLaIn bOrInG TeXt', user_id=message.sender.id
    )


def test_dont_process_old_dms(mocker, direct_messages, create_bot):
    ''' Test that the Twitter bot ignore the DMs sent before its start.
    '''

    mAPI = mocker.patch('tweepy.API')
    mAPI().direct_messages = direct_messages.get_message_list
    message = direct_messages.add_direct_message('previous message')

    class MyBot(Bot):
        'Echo bot'

        last_in_message = ''

        def default_response(self, in_message):
            self.last_in_message = in_message
            return in_message

    tep = TwitterEndpoint(
        consumer_key='', consumer_secret='',
        access_token='', access_token_secret=''
    )
    tep.set_polling_frequency(0.1)
    bot = create_bot(MyBot(), tep)

    message = direct_messages.add_direct_message('this is the first message')
    wait_for(lambda: bot.last_in_message == 'this is the first message')
    mAPI().send_direct_message.assert_called_once_with(
        'this is the first message', user_id=message.sender.id
    )

    message = direct_messages.add_direct_message('this is the last message')
    wait_for(lambda: bot.last_in_message == 'this is the last message')
    assert mAPI().send_direct_message.call_count == 2
    mAPI().send_direct_message.assert_called_with(
        'this is the last message', user_id=message.sender.id
    )


def test_twitter_commands(mocker, direct_messages, create_bot):
    ''' Test that the Twitter bot handles commands.
    '''

    mAPI = mocker.patch('tweepy.API')
    mAPI().direct_messages = direct_messages.get_message_list

    class MyBot(Bot):
        'Echo bot'

        start_called = False

        @command
        def start(self):
            self.start_called = True
            return 'Hello!'

    tep = TwitterEndpoint(
        consumer_key='', consumer_secret='',
        access_token='', access_token_secret=''
    )
    tep.set_polling_frequency(0.1)
    bot = create_bot(MyBot(), tep)

    message = direct_messages.add_direct_message('/start')
    wait_for(lambda: bot.start_called)
    mAPI().send_direct_message.assert_called_once_with(
        'Hello!', user_id=message.sender.id
    )


def test_use_start_on_twitter_follow(mocker, create_bot):
    ''' Twitter bot should auto-follow the followers and then use the start
        command.
    '''

    mAPI = mocker.patch('tweepy.API')

    class MyBot(Bot):
        'Echo bot'

        start_called = False

        @command
        def start(self):
            self.start_called = True
            return 'Hello new friend!'

    tep = TwitterEndpoint(
        consumer_key='', consumer_secret='',
        access_token='', access_token_secret=''
    )
    tep.set_polling_frequency(0.1)
    bot = create_bot(MyBot(), tep)

    follower_id = 42
    mAPI().followers_ids.return_value = [follower_id]
    wait_for(lambda: bot.start_called)
    mAPI().create_friendship.assert_called_once_with(
        user_id=follower_id
    )
    mAPI().send_direct_message.assert_called_once_with(
        'Hello new friend!', user_id=follower_id
    )
