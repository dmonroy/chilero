import asyncio
from aiohttp import web
from aiohttp.web_urldispatcher import UrlDispatcher


def dispatcher(cls, method):
    @asyncio.coroutine
    def f(request, *args, **kwargs):
        return getattr(cls(request, *args, **kwargs), method)()

    return f


class Application(web.Application):
    def __init__(self, routes=None, **kwargs):
        super(Application, self).__init__(**kwargs)

        for route in routes or []:
            for method in UrlDispatcher.METHODS:
                pattern = route[0]
                view = route[1]

                if callable(getattr(view, method.lower(), None)):
                    self.router.add_route(
                        method,
                        pattern,
                        dispatcher(view, method.lower()),
                        *route[2:]
                    )
