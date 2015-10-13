# flake8: noqa
import asyncio
import os

from .application import Application
from .response import JSONResponse, Response, HTMLResponse, JavaScriptResponse
from .view import View
from .resource import Resource


@asyncio.coroutine
def init(loop, cls, routes, *args, **kwargs): # pragma: no cover

    app = cls(*args, loop=loop, routes=routes, **kwargs)

    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = os.getenv('PORT', 8000)

    srv = yield from loop.create_server(app.make_handler(), HOST, PORT)

    return srv


def run(cls, routes, *args, **kwargs): # pragma: no cover
    """
    Run a web application.

    :param cls: Application class
    :param routes: list of routes
    :param args: additional arguments
    :param kwargs: additional keyword arguments
    :return: None
    """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init(loop, cls, routes, *args, **kwargs))

    try:
        loop.run_forever()
    except KeyboardInterrupt as e:
        loop.close()

    print('Process finished.')
