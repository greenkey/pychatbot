""" Unit tests for pychatbot.endpoints.TelegramEndpoint
"""

from pychatbot.bot import Bot
from pychatbot.endpoints import TwitterEndpoint


def test_twitter_interface(mocker):
    """ Test that the Twitter API is called when using the endpoint.
    """

    tweepyOAuth = mocker.patch('tweepy.OAuthHandler')
    tweepyAPI = mocker.patch('tweepy.API')

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
        access_token_secret=access_token_secret
    )
    bot.add_endpoint(endpoint)
    bot.run()

    tweepyOAuth.assert_called_once_with(consumer_key, consumer_secret)
    tweepyOAuth().set_access_token.assert_called_once_with(
        access_token, access_token_secret)
    tweepyAPI.assert_called_with(tweepyOAuth())

    bot.stop()
