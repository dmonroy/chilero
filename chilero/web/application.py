import os

import asyncio
from aiohttp import hdrs, web
from aiohttp.web_urldispatcher import UrlDispatcher
from chilero.web.resource import Resource


def dispatcher(cls, method):
    @asyncio.coroutine
    def f(request, *args, **kwargs):
        vkwargs = dict()
        for k in request.match_info.keys():
            vkwargs[k] = request.match_info.get(k)
        return getattr(cls(request, *args, **kwargs), method)(**vkwargs)

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

            object_pattern = r'%s' % os.path.join(pattern, view.id_pattern)

            patterns = {
                # Collection's actions to HTTP methods mapping
                pattern: dict(
                    index=[hdrs.METH_GET],
                    new=[hdrs.METH_POST, hdrs.METH_PUT],
                ),
                # Element's actions to HTTP methods mapping
                object_pattern: dict(
                    show=[hdrs.METH_GET],
                    update=[hdrs.METH_PUT, hdrs.METH_PATCH],
                    destroy=[hdrs.METH_DELETE]
                )

            }

            for pt, actions in patterns.items():
                for action, methods in actions.items():
                    if callable(getattr(view, action, None)):
                        for method in methods:
                            already_registered.append((pt, method.lower()))
                            self.router.add_route(
                                method, pt, dispatcher(view, action),
                                *route[2:]
                            )

        # HTTP methods as lowercase view methods
        for method in UrlDispatcher.METHODS:

            # Do not bind the same method twice
            if (pattern, method) in already_registered:  # pragma: no cover
                continue

            if callable(getattr(view, method.lower(), None)):
                self.router.add_route(
                    method,
                    pattern,
                    dispatcher(view, method.lower()),
                    *route[2:]
                    )
