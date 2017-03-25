import telegram


class TelegramEndpoint(object):

    def __init__(self, token):
        self._telegram = telegram.ext.Updater(token)
        self._token = token

    def set_bot(self, bot):
        self._bot = bot

    def run(self):
        self._telegram.start_polling()

    def stop(self):
        pass
