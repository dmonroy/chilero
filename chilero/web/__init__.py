# flake8: noqa
import asyncio
import os
import logging

import aiohttp.web

from .application import Application
from .response import JSONResponse, Response, HTMLResponse, JavaScriptResponse
from .view import View
from .resource import Resource


def init(cls, routes, *args, **kwargs): # pragma: no cover
    if 'loglevel' in kwargs:
        loglevel = kwargs.pop('loglevel')
    else:
        loglevel = logging.INFO

    logging.basicConfig(level=loglevel)
    app = cls(*args, routes=routes, **kwargs)
    return app


def run(cls, routes, *args, **kwargs): # pragma: no cover
    """
    Run a web application.

    :param cls: Application class
    :param routes: list of routes
    :param args: additional arguments
    :param kwargs: additional keyword arguments
    :return: None
    """

    app = init(cls, routes, *args, **kwargs)

    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 8000))

    aiohttp.web.run_app(app, port=PORT, host=HOST)


