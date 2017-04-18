""" Http endpoint for a pychatbot bot, use this to give your bot some REST API.
"""

from __future__ import absolute_import
from threading import Thread
from time import sleep
from socket import error as socket_error
from http.client import HTTPConnection
import logging
import os

try:  # specific imports for Python 3
    from urllib.parse import parse_qs
    from http.server import HTTPServer, BaseHTTPRequestHandler
except ImportError:  # specific imports for Python 2
    from urlparse import parse_qs
    from SocketServer import TCPServer as HTTPServer
    from SimpleHTTPServer import SimpleHTTPRequestHandler as BaseHTTPRequestHandler
    ConnectionRefusedError = socket_error
    HTTPServer.allow_reuse_address = True
import json


class _HttpHandler(BaseHTTPRequestHandler, object):
    """ Derived class of BaseHTTPRequestHandler, to handle the http requests
        of the HttpEndpoint http server.
    """
    bot = None

    def do_GET(self):
        """ Process GET requests.

            This method will process the requests in this form:

                `/command?parameter1=value1&...`

            It will use `in_message` parameter as the input message and reply
            with a JSON containing `out_message` propery:

                `{"out_message": "hello"}`
        """
        try:
            function, params = self.path.split("?")
            function, params = function[1:], parse_qs(params)
            self.send_response(200)
            self.end_headers()
            output = {
                "out_message": self.server.bot.process(
                    "".join(params["in_message"])
                )
            }
            self.wfile.write(json.dumps(output).encode("UTF-8"))
        except ValueError:
            # if no command is specified, serve the default html
            filename = os.path.join(
                os.path.dirname(__file__),
                'http',
                'index.html'
            )
            with open(filename, 'r') as f:
                self.send_response(200)
                self.end_headers()
                output = f.read()
            self.wfile.write(output)

    def log_message(self, format_, *args):
        """ Redefinition of the `log_message` method to use `logging` library.
        """
        logging.debug(format_, *args)


class HttpEndpoint(object):
    """ Http endpoint for a pychatbot bot, use this to give your bot some REST
        API.

        Example usage:

            >>> ep = HttpEndpoint()
            >>> bot.add_endpoint(ep)
            >>> bot.run()

        Then you can send message to the bot using simple GET requests:
        `http://localhost:8000/process?in_message=hello`

        Note: default port is 8000, if it is already used, `HttpEndpoint` will
        use the first free port after 8000 (8001, 8002...).

        The output using the example will be a json with the message:
        `{"out_message": "hello"}`
    """

    _host = "localhost"

    def __init__(self, port=8000):
        self.bot = None
        self._port = port

        try:
            self._httpd = HTTPServer(
                (self._host, self._port),
                _HttpHandler
            )
        except (OSError, socket_error) as e:
            raise e
            return None

        self._http_on = False
        self._http_thread = Thread(target=self.serve_loop)
        logging.info("Starting HTTP server on port %d", self._port)

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port

    def set_bot(self, bot):
        """ Sets the main bot, the bot must be an instance of
            `pychatbot.bot.Bot`.

            HttpEndpoint will use the bot to get the responses for the chat
            messages.
        """
        self.bot = bot
        self._httpd.bot = bot

    def serve_loop(self):
        """ Strats an infinite loop to process http requests.

            The loop ends when the `self._http_on` will be false (set `True` by
            `self.run` and `False` by `self.stop`)
        """
        try:
            while self._http_on:
                logging.debug("Ready for a new HTTP request...")
                self._httpd.handle_request()
        except socket_error:
            pass

    def run(self):
        """Starts the webserver to process requests (messages)."""
        self._http_on = True
        self._http_thread.start()

        while not self._http_thread.is_alive():
            sleep(0.5)

    def stop(self):
        """Stops the webserver."""
        self._http_on = False

        conn = HTTPConnection(
            self._host + ":" + str(self._port)
        )
        try:
            conn.request("GET", "/shutdown")
        except ConnectionRefusedError:
            pass
        conn.close()
        while self._http_thread.is_alive():
            sleep(0.5)
            self._httpd.server_close()
            self._httpd.socket.close()
