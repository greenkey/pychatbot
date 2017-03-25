import telegram

from pychatbot.bot import Bot, command
from endpoints.telegram import TelegramEndpoint


def test_telegram_interface_new(mocker):
	mocker.patch('telegram.ext.Updater')

	class MyBot(Bot):
		def default_response(self, in_message):
			return in_message.lower()

	bot = MyBot()

	ep = TelegramEndpoint(
		token='123:ABC'
	)
	bot.add_endpoint(ep)
	bot.run()

	telegram.ext.Updater.assert_called_once_with('123:ABC')
	assert telegram.ext.Updater().start_polling.called

def test_telegram_interface(mocker):
	
	class MyBot(Bot):
		def default_response(self, in_message):
			return in_message.lower()
			
	bot = MyBot()
	
	mocker.patch('telegram.ext.Updater')

	bot.telegram_serve(
		token='123:ABC'
	)
	
	telegram.ext.Updater.assert_called_once_with('123:ABC')
	assert telegram.ext.Updater().start_polling.called
	

def create_telegram_update(message_text):
	from datetime import datetime
	message=telegram.Message(
			message_id=0,
			from_user=telegram.User(0,'greenkey'),
			date=datetime.now(),
			chat=telegram.Chat(0,''),
			text=message_text
		)
	#message.reply_text = lambda x: x
	return telegram.Update(
		update_id=0,
		message=message
	)
	

def test_telegram_default_response_new(mocker):
	mocker.patch('telegram.ext.Updater')
	mocker.patch('telegram.ext.MessageHandler')
	mocker.patch('telegram.Message.reply_text')
	
	class MyBot(Bot):
		
		def default_response(self, in_message):
			return in_message[::-1].upper()
			
	bot = MyBot()
	ep = TelegramEndpoint(
		token='123:ABC'
	)
	bot.add_endpoint(ep)
	bot.run()
	
	handlers_added = [args for args, kwargs in telegram.ext.MessageHandler.call_args_list]
	assert len(handlers_added) > 0
	generic_handler = list(handler for filter_, handler in handlers_added)[-1]
	
	message = 'this is the message'
	generic_handler(bot, create_telegram_update(message))
	telegram.Message.reply_text.assert_called_with(bot.default_response(message))

	bot.stop()

def test_telegram_default_response(mocker):
	mocker.patch('telegram.ext.Updater')
	mocker.patch('telegram.ext.MessageHandler')
	mocker.patch('telegram.Message.reply_text')
	
	class MyBot(Bot):
		
		def default_response(self, in_message):
			return in_message[::-1].upper()
			
	bot = MyBot()
	bot.telegram_serve(
		token='123:ABC'
	)
	
	handlers_added = [args for args, kwargs in telegram.ext.MessageHandler.call_args_list]
	assert len(handlers_added) > 0
	generic_handler = list(handler for filter_, handler in handlers_added)[-1]
	
	message = 'this is the message'
	generic_handler(bot, create_telegram_update(message))
	telegram.Message.reply_text.assert_called_with(bot.default_response(message))


def test_telegram_command_new(mocker):
	mocker.patch('telegram.ext.Updater')
	mocker.patch('telegram.ext.CommandHandler')
	mocker.patch('telegram.Message.reply_text')

	class MyBot(Bot):

		def default_response(self, in_message):
			return in_message[::-1]

		@command
		def start(self):
			return 'start command has been called'

		@command
		def other(self):
			return 'other command has been called'

	bot = MyBot()
	ep = TelegramEndpoint(
		token='123:ABC'
	)
	bot.add_endpoint(ep)
	bot.run()

	commands_added = [args for args, kwargs in telegram.ext.CommandHandler.call_args_list]
	commands_added = dict((name, handler) for name, handler in commands_added)

	assert 'start' in commands_added
	assert 'other' in commands_added

	commands_added['start'](bot, create_telegram_update('/start'))
	telegram.Message.reply_text.assert_called_with(bot.start(bot))

	commands_added['other'](bot, create_telegram_update('/other'))
	telegram.Message.reply_text.assert_called_with(bot.other(bot))

def test_telegram_command(mocker):
	mocker.patch('telegram.ext.Updater')
	mocker.patch('telegram.ext.CommandHandler')
	mocker.patch('telegram.Message.reply_text')
	
	class MyBot(Bot):
		
		def default_response(self, in_message):
			return in_message[::-1]
		
		@command
		def start(self):
			return 'start command has been called'
	
		@command
		def other(self):
			return 'other command has been called'
	
	bot = MyBot()
	bot.telegram_serve(
		token='123:ABC'
	)
	
	commands_added = [args for args, kwargs in telegram.ext.CommandHandler.call_args_list]
	commands_added = dict((name, handler) for name, handler in commands_added)
	
	assert 'start','other' in commands_added
	
	commands_added['start'](bot, create_telegram_update('/start'))
	telegram.Message.reply_text.assert_called_with(bot.start(bot))
	
	commands_added['other'](bot, create_telegram_update('/other'))
	telegram.Message.reply_text.assert_called_with(bot.other(bot))
	

	



