"""A library to easily build chatbots."""


class Bot(object):
    """ The main class to create your bots.

        Use this class as a base for your bot and then add endpoints
        (services) to connect.

        Example usage:

            >>> class MyBot(Bot):
            ...     def default_response(self, in_message):
            ...         # setting echo as default response
            ...         return in_message
            ...     @command
            ...     def hello(self):
            ...             return "hello!"
            ...
            >>> bot = MyBot()
            >>> bot
            <__main__.MyBot object at 0x7f16e79f3940>
            >>> bot.process("repeat this")
            'repeat this'
            >>> bot.process("/hello") # the default command prepend is "/"
            'hello!'

        See documentation of the single functions to know all the capabilities.

    """

    def __init__(self):
        self.command_prepend = "/"
        self.endpoints = []

    @property
    def command_names(self):
        """ Retrieve the list of command names (string) defined for the class.

            To define a command in your bot, define a method adding the
            `@command` decorator.
        """
        for method_name in dir(self):
            if self._is_command(method_name):
                yield method_name

    def _is_command(self, command_name):
        """ Returns true if the Bot instance have a command named `command_name`
        """
        command = getattr(self, command_name)
        try:
            return callable(command) and command.is_command
        except AttributeError:
            return False

    def default_response(self, in_message):
        """ This method is called whenever a message is sent to the bot and
            the message is not a command (see `@command` decorator).

            Redefine this method in your bot class because it does nothing by
            default.
        """
        pass

    def process(self, in_message):
        """ This methos is called to process every message sent to the bot.

            The only purpose is to understand if it's a command or not and
            then to pass the message to the right method.
        """
        if (in_message.startswith(self.command_prepend) and
                in_message[1:] in self.command_names):
            command_handler = getattr(self, in_message[1:])
            return command_handler()
        return self.default_response(in_message)

    def add_endpoint(self, endpoint):
        """ Adds and endpoint to your bot object.

            Endpoints are services your bot needs to communicate, i.e.
            Telegram, Twitter...

            Example usage:

                >>> ep = TelegramEndpoint(
                ...     token='123:ABC'
                ... )
                >>> bot.add_endpoint(ep)

            Every endpoint has its own configuration so find your endpoint and
            look for needed information.

            pychatbot will take care of the rest: registering commands,
            getting messages, sending them...

        """
        endpoint.set_bot(self)
        self.endpoints.append(endpoint)

    def run(self):
        """ Call the endpoint's run method, to start receving messages and
            process them.
        """
        for endpoint in self.endpoints:
            endpoint.run()

    def stop(self):
        """ Stop the enpoint's polling/message receiving.ep
        """
        for endpoint in self.endpoints:
            endpoint.stop()


# decorator
def command(method):
    """ This is a decorator, put `@command` on top of the methods you want to
        set as command of your bot.

        Example usage:

            >>> class MyBot(Bot):
            ...     @command
            ...     def hello(self):
            ...             return "hello!"
            ...
            >>> bot = MyBot()
            >>> bot.process("/hello") # the default command prepend is "/"
            'hello!'

    """
    method.is_command = True
    return method
