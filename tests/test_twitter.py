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

    consumer_key = 'vAhDKzPPw9hfKE96S1dsXh0Tk',
    consumer_secret = 'gWmRZllJDrTVFOQrfeNLBe2A1mcMvE9bIw7XZNP3vk97U3rkrr',
    access_token = '852396996136763392-lbCvcphsCKf46qm56RFs6kkwC3AL5N4',
    access_token_secret = 'UrePBL8NXFpdoNSl4DBWxfvqvsYfQyafU0H3OgITOAkY9'

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
