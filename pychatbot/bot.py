class Bot(object):
    commands = []
    command_prepend = "/"
    endpoints = []

    def default_response(self, in_message):
        pass

    def process(self, in_message):
        if (in_message.startswith(self.command_prepend) and
                in_message[1:] in self.commands):
            f = self.__getattribute__(in_message[1:])
            return f(self)
        return self.default_response(in_message)

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
