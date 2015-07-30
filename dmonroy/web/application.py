import os

import asyncio
from aiohttp import web
from aiohttp.web_urldispatcher import UrlDispatcher
from dmonroy.web.resource import Resource


def dispatcher(cls, method):
    @asyncio.coroutine
    def f(request, *args, **kwargs):
        return getattr(cls(request, *args, **kwargs), method)()

    return f


class Application(web.Application):

    def __init__(self, routes=None, **kwargs):
        super(Application, self).__init__(**kwargs)

        for route in routes or []:
            self.register_routes(route)

    def register_routes(self, route):
        pattern = route[0]
        view = route[1]
        already_registered = []
        if issubclass(view, Resource):
            # Add resource actions as urls

            if callable(getattr(view, 'index', None)):
                already_registered.append('get')
                self.router.add_route(
                    'get',
                    pattern,
                    dispatcher(view, 'index'),
                    *route[2:]
                )

            if callable(getattr(view, 'new', None)):
                for method in ['post', 'put']:
                    already_registered.append(method)
                    self.router.add_route(
                        method,
                        pattern,
                        dispatcher(view, 'new'),
                        *route[2:]
                    )

            object_pattern = os.path.join(pattern, view.id_pattern)

            if callable(getattr(view, 'update', None)):
                self.router.add_route(
                    'patch',
                    object_pattern,
                    dispatcher(view, 'update'),
                    *route[2:]
                )

        # HTTP methods as lowercase view methods
        for method in UrlDispatcher.METHODS:

            # Do not bind the same method twice
            if method in already_registered:  # pragma: no cover
                continue

            if callable(getattr(view, method.lower(), None)):
                self.router.add_route(
                    method,
                    pattern,
                    dispatcher(view, method.lower()),
                    *route[2:]
                    )
