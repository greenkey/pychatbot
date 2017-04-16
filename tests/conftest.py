""" This module contains a set of utility to test pychatbot.

    cfr. http://pytest.org/2.2.4/plugins.html
"""

import pytest
from time import time, sleep


@pytest.fixture
def create_bot():
    """ Fixture - create the bot object given the bot_class and then add the
        endpoint object using the http_class.

        Using the fixture because at the end of the test the webserver is
        closed no matter the test outcome
    """

    fixture = dict()

    def create(bot, endpoint):
        """ The real function that creates the bot.

            This is needed because the fixture cannot accept parameters.
        """
        fixture['bot'] = bot
        fixture['ep'] = endpoint
        fixture['bot'].add_endpoint(fixture['ep'])
        fixture['bot'].run()

        return fixture['bot']

    yield create

    fixture['bot'].stop()


def wait_for(check_callback, polling_time=0.1, timeout=5):
    """ Creates an infinite loop, exit from it when the `check_callback` returns
        True.
        `polling_time` (seconds) is the time to wait between each try
        `timeout` (seconds) is the total time to wait before giving up
    """
    start = time()
    while time() - start < timeout:
        if check_callback():
            break
        sleep(polling_time)
    else:
        assert False
    assert True
