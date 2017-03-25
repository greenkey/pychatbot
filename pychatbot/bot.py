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

    def telegram_serve(self, token):
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

    def add_endpoint(self, endpoint):
        endpoint.set_bot(self)
        self.endpoints.append(endpoint)

    def run(self):
        for ep in self.endpoints:
            ep.run()

    def stop(self):
        for ep in self.endpoints:
            ep.stop()


# decorator    
class command():
    def __init__(self, f):
        Bot.commands.append(f.__name__)
        self.f = f

    def __call__(self, *args, **kwargs):
        return self.f(*args, **kwargs)
