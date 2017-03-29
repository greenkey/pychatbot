class Bot(object):

    def __init__(self):
        self.command_prepend = "/"
        self.endpoints = []

    @property
    def command_names(self):
        for method_name in dir(self):
            method = getattr(self, method_name)
            if callable(method):
                try:
                    if method.is_command:
                        yield method_name
                except AttributeError:
                    pass

    def default_response(self, in_message):
        pass

    def process(self, in_message):
        if (in_message.startswith(self.command_prepend) and
                in_message[1:] in self.command_names):
            f = getattr(self, in_message[1:])
            return f()
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
def command(method):
    method.is_command = True
    return method
