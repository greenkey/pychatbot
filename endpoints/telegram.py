import telegram


class TelegramEndpoint(object):

    def __init__(self, token):
        self._telegram = telegram.ext.Updater(token)
        self._token = token

    def set_bot(self, bot):
        self._bot = bot

        self._telegram.dispatcher.add_handler(
            telegram.ext.MessageHandler(
                telegram.ext.Filters.text,
                self.default_message_handler
            )
        )

    def run(self):
        self._telegram.start_polling()

    def stop(self):
        pass

    def default_message_handler(self, bot, update):
        in_message = update.message.text
        update.message.reply_text(self._bot.default_response(in_message))

