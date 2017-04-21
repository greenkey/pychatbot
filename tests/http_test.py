""" Not-so-unit tests for pychatbot.endpoints.HttpEndpoint
"""

from __future__ import absolute_import
import json
import requests
import pytest
from random import randint
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

from pychatbot.bot import Bot, command
from pychatbot.endpoints import HttpEndpoint


def send_to_http_bot(bot, in_message, port=None):
    """ Helper function: send a message to the bot using http
    """

    for endpoint in bot.endpoints:
        address = "http://%s:%d/process?%s" % (
            endpoint.host,
            port or endpoint.port,
            urlencode({"in_message": in_message})
        )

        return requests.get(address)


def test_http_interface(create_bot):
    """ Test that the http interface uses the bot with the given bot class
    """

    class MyBot(Bot):
        "Reverse bot"

        def default_response(self, in_message):
            return in_message[::-1]

    bot = create_bot(MyBot(), HttpEndpoint(port=randint(8000, 9000)))

    test_messages = ["hello", "another message"]
    for message in test_messages:
        resp = send_to_http_bot(bot, message)

        assert resp.status_code == 200
        ret = json.loads(resp.text)
        assert ret["out_message"] == message[::-1]


def test_http_command(create_bot):
    """ Test that the http interface correctly process commands
    """

    class MyBot(Bot):
        "Reverse bot, welcoming"

        def default_response(self, in_message):
            return in_message[::-1]

        @command
        def start(self):
            "Welcome the user as first thing!"
            return "Welcome!"

    bot = create_bot(MyBot(), HttpEndpoint(port=randint(8000, 9000)))

    resp = send_to_http_bot(bot, "/start")

    assert resp.status_code == 200
    ret = json.loads(resp.text)
    assert ret["out_message"] == "Welcome!"


def test_exception_using_same_port(create_bot):
    """ Starts two bots on the same port, the second should not start and raise
        and exception.
    """

    bot1 = create_bot(Bot(), HttpEndpoint(port=8046))

    with pytest.raises(Exception):
        # not using fixture because otherwise I won't get the exception
        bot2 = Bot()
        endpoint2 = HttpEndpoint(port=8046)
        bot2.add_endpoint(endpoint2)
        bot2.run()

    resp = send_to_http_bot(bot1, "/start")
    assert resp.status_code == 200

    resp = send_to_http_bot(bot2, "/start")
    assert resp is None

    bot1.stop()


def test_uses_a_custom_port():
    """ Start the webserver on a port specified, then try to send messages to
        that port.
    """

    bot = Bot()
    endpoint = HttpEndpoint(port=8045)
    bot.add_endpoint(endpoint)
    bot.run()

    resp = send_to_http_bot(bot, "/start", port=8045)
    assert resp.status_code == 200

    bot.stop()


def test_expose_html_page(create_bot):
    """ Starting the bot, an HTML page is available in the root of the webserver
        showing a form to chat with the bot.
    """

    endpoint = HttpEndpoint(port=randint(8000, 9000))
    create_bot(Bot(), endpoint)

    address = "http://%s:%d/" % (endpoint.host, endpoint.port)

    response = requests.get(address)

    assert 'html' in response.text.lower()
