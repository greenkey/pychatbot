eddie
=========

.. image:: https://badges.gitter.im/eddie-py/Lobby.svg
   :alt: Join the chat at https://gitter.im/eddie-py/Lobby
   :target: https://gitter.im/eddie-py/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge

|Build Status|

``eddie`` is a library you can use to create your own chat bots in
seconds.

This is a very young library, any request/suggestion/help will be very
appreciated. For them, create an issue or contact me!

Install
-------

You can install eddie using just pip:

.. code:: shell

    $ pip install eddie

If you want the latest version download this repository in your project or
using pip:

.. code:: shell

    $ pip install git+https://github.com/greenkey/eddie.git

Usage
-----

You have to define your bot class, extending the default ``Bot`` class:

.. code:: python

    >>> from eddie.bot import Bot
    >>> class MyBot(Bot):
    ...     pass
    ... 
    >>> b = MyBot()
    >>> b
    <__main__.MyBot object at 0x7f16e79f3940>

Of course you'll want to define some bahaviour, the following chapters
teach you how to do it.

Defining a default response
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    >>> from eddie.bot import Bot
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

Defining commands
~~~~~~~~~~~~~~~~~

Just define a method of your Bot class using the ``command`` decorator.

.. code:: python

    >>> from eddie.bot import Bot, command
    >>> class MyBot(Bot):
    ...     @command
    ...     def hello(self):
    ...             return "hello!"
    ... 
    >>> bot = MyBot()
    >>> bot.process("/hello") # the default command prepend is "/"
    'hello!'

Defining interfaces
~~~~~~~~~~~~~~~~~~~

A bot running in local would be pretty useless, isn't it?

The simplest interface we can give to our bot is the http one.

.. code:: python

    >>> from eddie.bot import Bot
    >>> from eddie.endpoints import HttpEndpoint
    >>> class MyBot(Bot):
    ...     def default_response(self, in_message):
    ...             return in_message
    ... 
    >>> bot = MyBot()
    >>> ep = HttpEndpoint()
    >>> bot.add_endpoint(ep)
    >>> bot.run()

Then you can send message to the bot using simple GET requests:
``http://localhost:8000/process?in_message=hello``

Note: default port is 8000, if it is already used, ``HttpEndpoint`` will
use the first free port after 8000 (8001, 8002...).

The output using the example will be a json with the message:
``{"out_message": "hello"}``

Telegram
~~~~~~~~

Yes, you can easily connect your bot with the Telegram API, thanks to
the
`python-telegram-bot <https://github.com/python-telegram-bot/python-telegram-bot>`__
library.

You don't have to worry about nothing, except getting a token from the
`BotFather <https://core.telegram.org/bots#botfather>`__ and passing it
to your bot.

.. code:: python

    >>> from eddie.bot import Bot
    >>> from eddie.endpoints import TelegramEndpoint
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

Twitter
~~~~~~~~

It's not a proper bot framework, but with ``eddie`` you can have a bot in
Twitter too, thanks to the `tweepy <https://github.com/tweepy/tweepy>`__
library.

Just follow the instrunction on `how to create a Twitter App <https://apps.twitter.com/app/new>`__
, get all the tokens and use them to instantiate the ``TwitterEndpoint``.

.. code:: python

    >>> from eddie.bot import Bot
    >>> from eddie.endpoints import TwitterEndpoint
    >>> class MyBot(Bot):
    ...     def default_response(self, in_message):
    ...             return in_message
    ... 
    >>> bot = MyBot()
    >>> ep = TwitterEndpoint(
    ...     consumer_key='your consumer_key',
    ...     consumer_secret='your consumer_secret',
    ...     access_token='your access_token',
    ...     access_token_secret='your access_token_secret'
    ... )
    >>> bot.add_endpoint(ep)
    >>> bot.run()

Logging
~~~~~~~

This library uses the logging module. To set up logging to standard
output, put:

.. code:: python

    import logging
    logging.basicConfig(level=logging.DEBUG)

at the beginning of your script.

Get involved
------------

If you want to contribute, download the repository, then:

.. code:: shell

    $ virtualenv ~/.venv/eddie # not required but highly suggested
    $ source ~/.venv/eddie/bin/activate
    $ pip install -r requirements-dev.txt # install all the requirements
    $ pytest

.. |Build Status| image:: https://travis-ci.org/greenkey/eddie.svg?branch=master
   :target: https://travis-ci.org/greenkey/eddie
