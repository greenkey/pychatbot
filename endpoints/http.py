from threading import Thread
from time import sleep

try:
    from urllib.parse import parse_qs
    from http.server import HTTPServer, BaseHTTPRequestHandler
except ImportError:
    from urlparse import parse_qs
    import SimpleHTTPServer
    from SocketServer import TCPServer as HTTPServer
    from SimpleHTTPServer import SimpleHTTPRequestHandler as BaseHTTPRequestHandler
    HTTPServer.allow_reuse_address = True
import json


class HttpEndpoint(object):
    _PORT = 8000
    _ADDRESS = ""

    def __init__(self):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(s):
                function, params = s.path.split("?")
                function, params = function[1:], parse_qs(params)

                s.send_response(200)
                s.end_headers()
                output = {
                    "out_message": self._bot.process("".join(params["in_message"]))
                }
                s.wfile.write(json.dumps(output).encode("UTF-8"))

        self._httpd = HTTPServer((self._ADDRESS, self._PORT), Handler)
        self._http_on = False

    def set_bot(self, bot):
        self._bot = bot

    def serve_loop(self):
        while self._http_on:
            self._httpd.handle_request()

    def start(self):
        self._http_on = True
        self._http_thread = Thread(target=self.serve_loop)
        self._http_thread.daemon = True
        self._http_thread.start()

        while not self._http_thread.is_alive():
            sleep(1)

    def stop(self):
        self._http_on = False

        while self._http_thread.is_alive():
            self._httpd.server_close()
