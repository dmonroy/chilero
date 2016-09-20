import asyncio
import socket
import unittest
from functools import wraps

from aiohttp import log
from chilero import web


def asynctest(f):

    @wraps(f)
    def wrapper(*args, **kwargs):
        @asyncio.coroutine
        def go():
            yield from f(*args, **kwargs)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(go())
    return wrapper


class WebTestCase(unittest.TestCase):
    application = web.Application
    routes = []

    @asyncio.coroutine
    def initialize_application(self):
        return self.application(self.routes, loop=self.loop)

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        @asyncio.coroutine
        def go():
            self.app = yield from self.initialize_application()
            yield from self.create_server()

        self.loop.run_until_complete(go())

    def tearDown(self):
        self.app.finish()
        self.loop.close()

    @asyncio.coroutine
    def create_server(self):
        if hasattr(self, 'port'):
            return  # pragma: no cover

        app = getattr(self, 'app')
        assert app is not None, 'Application not initialized'

        self.port = self.find_unused_port()

        self.handler = app.make_handler(
            keep_alive_on=False,
            access_log=log.access_logger)
        self.server = yield from self.loop.create_server(
            self.handler, '127.0.0.1', self.port)

    def full_url(self, path):
        return 'http://127.0.0.1:{}{}'.format(self.port, path)

    def find_unused_port(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('127.0.0.1', 0))
        port = s.getsockname()[1]
        s.close()
        return port
