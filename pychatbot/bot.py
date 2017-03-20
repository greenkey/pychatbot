import json

class Bot(object):
	commands = []
	command_prepend = "/"
	endpoints = []
	
	def default_response(self, in_message):
		pass
    
	def process(self, in_message):
		if in_message.startswith(self.command_prepend) and in_message[1:] in self.commands:
			f = self.__getattribute__(in_message[1:])
			return f(self)
		return self.default_response(in_message)


	def http_serve(self):
		from http.server import HTTPServer, BaseHTTPRequestHandler
		import http
		from threading import Thread
		try:
			from urllib.parse import parse_qs
		except ImportError:
			from urlparse import parse_qs

		PORT = 8000

		class Handler(BaseHTTPRequestHandler):
			def do_GET(s):
				
				function, params = s.path.split("?")
				function, params = function[1:], parse_qs(params)
				
				s.send_response(200)
				s.end_headers()
				output = {
					"out_message": self.process("".join(params["in_message"]))
				}
				s.wfile.write(json.dumps(output).encode("UTF-8"))
				
		def serve_loop():
			while self.http_on:
				self.httpd.handle_request()

		self.httpd = HTTPServer(('', PORT), Handler)
		self.http_on = True
		self.http_thread = Thread(target=serve_loop)
		self.http_thread.daemon = True
		self.http_thread.start()
		
		while not self.http_thread.is_alive():
			pass
		

	def http_stop(self):
		self.http_on = False

		while self.http_thread.is_alive():
			self.httpd.server_close()
			

	def telegram_serve(self,token):
		from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
		
		self.telegram = Updater(token)
		
		# commands

		def telegram_command_handler(bot, update):
			command = update.message.text[1:]
			f = self.__getattribute__(command)
			update.message.reply_text(f(self))
		self.telegram_command_handler = telegram_command_handler
		
		for command in self.commands:
			self.telegram.dispatcher.add_handler(
				CommandHandler(
					command,
					self.telegram_command_handler
				)
			)
		
		# default message handler
		
		def telegram_message_handler(bot, update):
			message = update.message.text
			update.message.reply_text(self.default_response(message))
		self.telegram_message_handler = telegram_message_handler
			
		self.telegram.dispatcher.add_handler(
			MessageHandler(
				Filters.text,
				self.telegram_message_handler
			)
		)
		
		self.telegram.start_polling()


	def add_endpoint(self,endpoint):
		self.endpoints.append(endpoint)


	def start(self):
		for ep in self.endpoints:
			ep.start()


# decorator    
class command():

	def __init__(self, f):
		Bot.commands.append(f.__name__)
		self.f = f

	def __call__(self, *args, **kwargs):
		return self.f(*args, **kwargs)
