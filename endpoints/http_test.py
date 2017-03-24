from __future__ import absolute_import
from http.client import HTTPConnection
import json
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

from pychatbot.bot import Bot
from endpoints.http import HttpEndpoint


def test_http_interface_new():
    class MyBot(Bot):
        def default_response(self, in_message):
            return in_message[::-1]

    bot = MyBot()
    ep = HttpEndpoint()
    bot.add_endpoint(ep)
    bot.start()

    test_messages = ["hello", "another message"]
    for tm in test_messages:
        conn = HTTPConnection("127.0.0.1:8000")
        conn.request("GET", "/process?" + urlencode({"in_message": tm}))
        r = conn.getresponse()
        assert r.status == 200
        ret = json.loads(r.read().decode())
        assert ret["out_message"] == tm[::-1]
        conn.close()

    bot.stop()
