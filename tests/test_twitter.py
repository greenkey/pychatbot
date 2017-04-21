''' Unit tests for pychatbot.endpoints.TelegramEndpoint
'''

import pytest
import json
from tweepy.models import ModelFactory

from pychatbot.bot import Bot, command
from pychatbot.endpoints import TwitterEndpoint


class TweepyMocker:
    """ Fixture to create fake DirectMessages
    """

    def __init__(self):
        self.tweepy_endpoint = None
        self.tweepy_api = None
        self.direct_messages_created = []
        self.followers = []
        self.friends = []

    def set_endpoint(self, tweepy_endpoint):
        self.tweepy_endpoint = tweepy_endpoint

    def set_API(self, tweepy_api):
        tweepy_api().followers_ids = self.get_followers_ids
        tweepy_api().friends_ids = self.get_friends_ids
        tweepy_api().create_friendship.side_effect = self.create_friendship

        self.tweepy_api = tweepy_api

    def get_followers_ids(self):
        return [f.id for f in self.followers]

    def get_friends_ids(self):
        return [f.id for f in self.friends]

    def create_friendship(self, user_id):
        if user_id not in self.get_friends_ids():
            for user in self.followers:
                if user.id == user_id:
                    self.followers.remove(user)
                    new_user = user
                    break
            else:
                new_user = ModelFactory.user.parse(
                    self.tweepy_api,
                    {'id': user_id, 'screen_name': 'user #%d' % user_id}
                )

            self.friends.append(new_user)

    def add_to_stream(self, data):
        try:
            self.tweepy_endpoint._stream.listener.on_data(
                json.dumps(data)
            )
        except AttributeError:
            # if the endoipoint doesn't have the _stream or the listener yet
            # it means it's not listening
            pass

    def add_direct_message(self, text):
        """ Create a fake DirectMessage, adds it to `self.direct_messages`,
            calls on_data of the stream lisstener and then returns the message
        """

        new_dm = {
            'id': len(self.direct_messages_created) + 1,
            'text': text,
            'sender': {
                'id': 0,
                'screen_name': 'greenkey',
                'name': 'greenkey'
            },
            'sender_screen_name': 'greenkey'
        }

        self.direct_messages_created.append(new_dm)

        self.add_to_stream({'direct_message': new_dm})

        return new_dm

    def add_follower(self, screen_name):
        """ Adds a follower to the list of followers, calls the on_data method
            of the stream listener
        """

        data = {
            "event": "follow",
            "source": {
                "id": len(self.followers) + 1,
                "screen_name": screen_name,
            },
            "target": {
                "id": 852396996136763392,
                "screen_name": "pychatbot",
            }
        }

        self.followers.append(
            ModelFactory.user.parse(
                self.tweepy_api,
                data['source']
            )
        )

        self.add_to_stream(data)

        return data['source']


@pytest.fixture()
def twit_mock():
    """ Fixture: returns `DirectMessageMocker`, all the logic is in the class
        definition.
    """
    return TweepyMocker()


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

    bot = create_bot(MyBot(), tep)

    assert bot.endpoints[0]._bot == bot

    mOAuthHandler.assert_called_once_with(consumer_key, consumer_secret)
    mOAuthHandler().set_access_token.assert_called_once_with(
        access_token, access_token_secret
    )
    mAPI.assert_called_once_with(mOAuthHandler())


def test_twitter_default_response(mocker, twit_mock, create_bot):
    ''' Test that the Twitter bot correctly reply with the default response.
    '''

    mAPI = mocker.patch('tweepy.API')
    mocker.patch('tweepy.StreamListener')

    class MyBot(Bot):
        'Upp&Down bot'

        def default_response(self, in_message):
            return ''.join([
                c.upper() if i % 2 else c.lower()
                for i, c in enumerate(in_message)
            ])

    tep = TwitterEndpoint(
        consumer_key='', consumer_secret='',
        access_token='', access_token_secret=''
    )
    twit_mock.set_endpoint(tep)
    create_bot(MyBot(), tep)

    message = twit_mock.add_direct_message('SuperCamelCase')
    mAPI().send_direct_message.assert_called_with(
        text='sUpErCaMeLcAsE', user_id=message['sender']['id']
    )

    message = twit_mock.add_direct_message('plain boring text')
    mAPI().send_direct_message.assert_called_with(
        text='pLaIn bOrInG TeXt', user_id=message['sender']['id']
    )


def test_dont_process_old_dms(mocker, twit_mock, create_bot):
    ''' Test that the Twitter bot ignore the DMs sent before its start.
    '''

    mAPI = mocker.patch('tweepy.API')

    class MyBot(Bot):
        'Echo bot'

        def default_response(self, in_message):
            return in_message

    tep = TwitterEndpoint(
        consumer_key='', consumer_secret='',
        access_token='', access_token_secret=''
    )
    twit_mock.set_endpoint(tep)

    twit_mock.add_direct_message('previous message')

    create_bot(MyBot(), tep)

    message = twit_mock.add_direct_message('this is the first message')
    mAPI().send_direct_message.assert_called_once_with(
        text='this is the first message', user_id=message['sender']['id']
    )

    message = twit_mock.add_direct_message('this is the last message')
    assert mAPI().send_direct_message.call_count == 2
    mAPI().send_direct_message.assert_called_with(
        text='this is the last message', user_id=message['sender']['id']
    )


def test_twitter_commands(mocker, twit_mock, create_bot):
    ''' Test that the Twitter bot handles commands.
    '''

    mAPI = mocker.patch('tweepy.API')

    class MyBot(Bot):
        'Echo bot'

        @command
        def start(self):
            return 'Hello!'

    tep = TwitterEndpoint(
        consumer_key='', consumer_secret='',
        access_token='', access_token_secret=''
    )
    twit_mock.set_endpoint(tep)
    create_bot(MyBot(), tep)

    message = twit_mock.add_direct_message('/start')
    mAPI().send_direct_message.assert_called_once_with(
        text='Hello!', user_id=message['sender']['id']
    )


def test_use_start_on_twitter_follow(mocker, twit_mock, create_bot):
    ''' Twitter bot should auto-follow the followers and then use the start
        command.
    '''

    mAPI = mocker.patch('tweepy.API')
    twit_mock.set_API(mAPI)

    class MyBot(Bot):
        'Echo bot'

        @command
        def start(self):
            return 'Hello new friend!'

    tep = TwitterEndpoint(
        consumer_key='', consumer_secret='',
        access_token='', access_token_secret=''
    )
    twit_mock.set_endpoint(tep)
    create_bot(MyBot(), tep)

    user = twit_mock.add_follower('new_friend')

    mAPI().create_friendship.assert_called_once_with(
        user_id=user['id']
    )
    mAPI().send_direct_message.assert_called_once_with(
        text='Hello new friend!', user_id=user['id']
    )


def test_follow_new_followers_at_boot(mocker, twit_mock, create_bot):
    ''' Twitter bot should check the follower at start and follow the new ones.
    '''

    mAPI = mocker.patch('tweepy.API')
    twit_mock.set_API(mAPI)

    class MyBot(Bot):
        'Echo bot'

        @command
        def start(self):
            return 'Hello new friend!'

    tep = TwitterEndpoint(
        consumer_key='', consumer_secret='',
        access_token='', access_token_secret=''
    )
    twit_mock.set_endpoint(tep)
    user = twit_mock.add_follower('new_friend')

    create_bot(MyBot(), tep)

    mAPI().create_friendship.assert_called_once_with(
        user_id=user['id']
    )
    mAPI().send_direct_message.assert_called_once_with(
        text='Hello new friend!', user_id=user['id']
    )


def test_dont_send_message_if_already_following(mocker, twit_mock, create_bot):
    ''' Twitter bot should check the follower at start and follow the new ones.
    '''

    mAPI = mocker.patch('tweepy.API')
    twit_mock.set_API(mAPI)

    class MyBot(Bot):
        'Echo bot'

        @command
        def start(self):
            return 'Hello new friend!'

    tep = TwitterEndpoint(
        consumer_key='', consumer_secret='',
        access_token='', access_token_secret=''
    )
    twit_mock.set_endpoint(tep)
    user = twit_mock.add_follower('new_friend')
    twit_mock.create_friendship(user['id'])

    create_bot(MyBot(), tep)

    mAPI().create_friendship.assert_not_called()
    mAPI().send_direct_message.assert_not_called()
