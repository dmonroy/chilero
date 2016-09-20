import asyncio
import os
from functools import wraps

from aiohttp import hdrs, web
from chilero.web.resource import Resource


class Application(web.Application):

    def __init__(self, routes=None, **kwargs):
        super(Application, self).__init__(**kwargs)

        for route in routes or []:
            self.register_routes(route)

    def dispatcher(self, cls, method, parent=None):
        @wraps(getattr(cls, method))
        @asyncio.coroutine
        def f(request, *args, **kwargs):
            vkwargs = dict()
            for k in request.match_info.keys():
                vkwargs[k] = request.match_info.get(k)
            return getattr(
                cls(request, self, *args, parent=parent, **kwargs), method
            )(**vkwargs)

        return f

    def register_routes(self, route, parent=None):
        pattern = route[0]
        view = route[1]

        # remove trailing slash
        if pattern.endswith('/') and len(pattern) > 1:
            pattern = pattern[:-1]

        if issubclass(view, Resource):
            # Add resource actions as urls

            url_name = route[2] \
                if len(route) == 3 \
                else view.resource_name \
                if hasattr(view, 'resource_name') \
                else view.__name__.lower()

            object_pattern = r'%s' % os.path.join(pattern, view.id_pattern)

            definition_url_name = '{}_definition'.format(url_name)
            if definition_url_name not in self.router and (
                    hasattr(view, 'definition') or
                    hasattr(view, 'get_definition')
                    ):

                definition_pattern = r'{}'.format(
                    os.path.join(pattern, '+definition')
                )
                self.router.add_route(
                    'GET',
                    definition_pattern,
                    self.dispatcher(view, 'resource_definition'),
                    name=definition_url_name
                )

            # Nested resources
            for nkey, nview in (
                    view.nested_collection_resources or {}
            ).items():
                self.register_routes(
                    [
                        os.path.join(
                            pattern if pattern != '/' else '',
                            nkey
                        ),
                        nview
                    ], parent='{}_index'.format(url_name)
                )

            for nkey, nview in (view.nested_entity_resources or {}).items():
                self.register_routes(
                    [
                        os.path.join(
                            object_pattern.replace(
                                '{id}', '{%s_id}' % url_name
                            ),
                            nkey
                        ),
                        nview
                    ], parent='{}_item'.format(url_name)
                )

            patterns = {
                # Collection's actions to HTTP methods mapping
                pattern: dict(
                    index=[hdrs.METH_GET],
                    new=[hdrs.METH_POST, hdrs.METH_PUT],
                    collection_options=[hdrs.METH_OPTIONS]
                ),
                # Element's actions to HTTP methods mapping
                object_pattern: dict(
                    show=[hdrs.METH_GET],
                    update=[hdrs.METH_PUT, hdrs.METH_PATCH],
                    destroy=[hdrs.METH_DELETE],
                    entity_options=[hdrs.METH_OPTIONS]
                )

            }

            for pt, actions in patterns.items():
                for action, methods in actions.items():
                    if callable(getattr(view, action, None)):
                        for method in methods:
                            name = '{}_{}'.format(
                                url_name, 'index' if pt == pattern else 'item'
                            )

                            name = None if name in self.router else name

                            self.router.add_route(
                                method, pt, self.dispatcher(
                                    view, action, parent=parent
                                ),
                                name=name
                            )

        else:
            # Its a basic view
            url_name = route[2] \
                if len(route) == 3 \
                else view.__name__.lower()

            # HTTP methods as lowercase view methods
            for method in hdrs.METH_ALL | {hdrs.METH_ANY}:
                if callable(getattr(view, method.lower(), None)):
                    # Do not bind the same method twice

                    name = url_name

                    name = None if name in self.router else url_name

                    self.router.add_route(
                        method,
                        pattern,
                        self.dispatcher(view, method.lower()),
                        name=name
                    )

    def reverse(self, name, query=None, **kwargs):
        assert name in self.router, "Url '{}' doesn't exists!".format(name)
        if kwargs:
            return self.router[name].url(parts=kwargs, query=query)
        else:
            return self.router[name].url(query=query)
