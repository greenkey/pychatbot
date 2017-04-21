# pychatbot

[![Build Status](https://travis-ci.org/greenkey/pychatbot.svg?branch=master)](https://travis-ci.org/greenkey/pychatbot)


`pychatbot` is a library you can use to create your own chat bots in seconds.

This is a very young library, any request/suggestion/help will be very
appreciated. For them, create an issue or contact me!

## Install

You can install it downloading this repository in your project or using pip:
```shell
$ pip install git+https://github.com/greenkey/pychatbot.git
```

A package in the PyPI repository will be available soon.

## Usage

You have to define your bot class, extending the default `Bot` class:
```python
>>> from pychatbot.bot import Bot
>>> class MyBot(Bot):
...     pass
... 
>>> b = MyBot()
>>> b
<__main__.MyBot object at 0x7f16e79f3940>

```

Of course you'll want to define some bahaviour, the following chapters teach you how to do it.

### Defining a default response

```python
>>> from pychatbot.bot import Bot
>>> class MyBot(Bot):
...     def default_response(self, in_message):
...         # setting echo as default response
...         return in_message
... 
>>> b = MyBot()
>>> b.process("Hello!")
'Hello!'
>>> b.process("Goodbye!")
'Goodbye!'
```

### Defining commands

Just define a method of your Bot class using the `command` decorator.

```python
>>> from pychatbot.bot import Bot, command
>>> class MyBot(Bot):
...     @command
...     def hello(self):
...             return "hello!"
... 
>>> bot = MyBot()
>>> bot.process("/hello") # the default command prepend is "/"
'hello!'
```

### Defining interfaces

A bot running in local would be pretty useless, isn't it?

The simplest interface we can give to our bot is the http one.

```python
>>> from pychatbot.bot import Bot
>>> from pychatbot.endpoints import HttpEndpoint
>>> class MyBot(Bot):
...     def default_response(self, in_message):
...             return in_message
... 
>>> bot = MyBot()
>>> ep = HttpEndpoint()
>>> bot.add_endpoint(ep)
>>> bot.run()
```

Then you can send message to the bot using simple GET requests: `http://localhost:8000/process?in_message=hello`

Note: default port is 8000, if it is already used, `HttpEndpoint` will use the first free port after 8000 (8001, 8002...).

The output using the example will be a json with the message: `{"out_message": "hello"}`

### Telegram

Yes, you can easily connect your bot with the Telegram API, thanks to
the [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
library.

You don't have to worry about nothing, except getting a token from the
[BotFather](https://core.telegram.org/bots#botfather) and passing it
to your bot.

```python
>>> from pychatbot.bot import Bot
>>> from pychatbot.endpoints import TelegramEndpoint
>>> class MyBot(Bot):
...     def default_response(self, in_message):
...             return in_message
... 
>>> bot = MyBot()
>>> ep = TelegramEndpoint(
...     token='123:ABC'
... )
>>> bot.add_endpoint(ep)
>>> bot.run()
```


### Logging

This library uses the logging module. To set up logging to standard output, put:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

at the beginning of your script.


## Get involved

If you want to contribute, download the repository, then:

```shell
$ virtualenv ~/.venv/pychatbot # not required but highly suggested
$ source ~/.venv/pychatbot/bin/activate
$ pip install -r requirements-dev.txt # install all the requirements
$ pytest
```
