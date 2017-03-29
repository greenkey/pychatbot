from pychatbot.bot import Bot


def test_create_bot_object():
    b = Bot()
    assert isinstance(b, Bot)


def test_default_behaviour():
    class MyBot(Bot):
        def default_response(self, in_message):
            return in_message

    bot = MyBot()
    assert bot.process("hello") == "hello"
    assert bot.process("123") == "123"
    assert bot.process("/hello") == "/hello"


def test_add_command():
    from pychatbot.bot import command

    class MyBot(Bot):
        @command
        def hello(self):
            return "hello!"

        @command
        def bye(self):
            return "goodbye..."

    bot = MyBot()
    assert bot.process("/hello") == "hello!"
    assert bot.process("/bye") == "goodbye..."


def test_add_endpoint_start_stop(mocker):
    class MyBot(Bot):
        pass

    endpoint = mocker.Mock()

    bot = MyBot()
    bot.add_endpoint(endpoint)
    bot.run()

    assert endpoint.run.called

    bot.stop()

    assert endpoint.stop.called
