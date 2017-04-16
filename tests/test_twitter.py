''' Unit tests for pychatbot.endpoints.TelegramEndpoint
'''

import pytest
from twitter.models import DirectMessage, User

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

    twitterAPI = mocker.patch('twitter.Api')

    class MyBot(Bot):
        'Lowering bot'

        def default_response(self, in_message):
            return in_message.lower()

    consumer_key = 'consumer_key',
    consumer_secret = 'consumer_secret',
    access_token = 'access_token',
    access_token_secret = 'access_token_secret'

    bot = create_bot(MyBot(), TwitterEndpoint(
        consumer_key=consumer_key, consumer_secret=consumer_secret,
        access_token=access_token, access_token_secret=access_token_secret
    ))
    bot.endpoints[0].set_polling_frequency(0.1)

    assert bot.endpoints[0]._bot == bot

    twitterAPI.assert_called_once_with(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token_key=access_token,
        access_token_secret=access_token_secret
    )


def test_twitter_default_response(mocker, direct_messages, create_bot):
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

    bot = create_bot(MyBot(), TwitterEndpoint(
        consumer_key='', consumer_secret='',
        access_token='', access_token_secret=''
    ))
    bot.endpoints[0].set_polling_frequency(0.1)

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


def test_dont_process_old_dms(mocker, direct_messages, create_bot):
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

    bot = create_bot(MyBot(), TwitterEndpoint(
        consumer_key='', consumer_secret='',
        access_token='', access_token_secret=''
    ))
    bot.endpoints[0].set_polling_frequency(0.1)

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


def test_twitter_commands(mocker, direct_messages, create_bot):
    ''' Test that the Twitter bot handles commands.
    '''

    twitterAPI = mocker.patch('twitter.Api')
    twitterAPI().GetDirectMessages = direct_messages.get_message_list

    class MyBot(Bot):
        'Echo bot'

        start_called = False

        @command
        def start(self):
            self.start_called = True
            return 'Hello!'

    bot = create_bot(MyBot(), TwitterEndpoint(
        consumer_key='', consumer_secret='',
        access_token='', access_token_secret=''
    ))
    bot.endpoints[0].set_polling_frequency(0.1)

    message = direct_messages.add_direct_message('/start')
    wait_for(lambda: bot.start_called)
    twitterAPI().PostDirectMessage.assert_called_once_with(
        'Hello!', user_id=message.sender.id
    )

    bot.stop()


def test_use_start_on_twitter_follow(mocker, create_bot):
    ''' Twitter bot should auto-follow the followers and then use the start
        command.
    '''

    twitterAPI = mocker.patch('twitter.Api')

    class MyBot(Bot):
        'Echo bot'

        start_called = False

        @command
        def start(self):
            self.start_called = True
            return 'Hello new friend!'

    bot = create_bot(MyBot(), TwitterEndpoint(
        consumer_key='', consumer_secret='',
        access_token='', access_token_secret=''
    ))
    bot.endpoints[0].set_polling_frequency(0.1)

    follower = create_fake_user()
    twitterAPI().IncomingFriendship.return_value = [follower]
    wait_for(lambda: bot.start_called)
    twitterAPI().CreateFriendship.assert_called_once_with(
        user_id=follower.id
    )
    twitterAPI().PostDirectMessage.assert_called_once_with(
        'Hello new friend!', user_id=follower.id
    )

    bot.stop()
