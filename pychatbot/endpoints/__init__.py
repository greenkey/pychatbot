""" This module is meant to contain all the endpoints class.

	An endpoint is a connection to a bot service, i.e.: Telegram, Facebook
	Messenger, Twitter, Slack...
"""

from .http import HttpEndpoint
from .telegram import TelegramEndpoint
from .twitter import TwitterEndpoint
