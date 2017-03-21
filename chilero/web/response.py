import json

from aiohttp import web


class Response(web.Response):
    def __init__(self, body=None, **kwargs):
        super(Response, self).__init__(
            body=body.encode('utf-8') if body is not None else body, **kwargs
        )


class JavaScriptResponse(Response):

    def __init__(self, data, **kwargs):
        super(JavaScriptResponse, self).__init__(
            body=json.dumps(data), content_type='application/javascript',
            **kwargs
        )


class JSONResponse(Response):

    def __init__(self, data, cls=None, **kwargs):
        super(JSONResponse, self).__init__(
            body=json.dumps(data, indent=4, cls=cls),
            content_type='application/json', **kwargs
        )


class HTMLResponse(Response):

    def __init__(self, body, **kwargs):
        super(HTMLResponse, self).__init__(
            body=body, content_type='text/html', **kwargs
        )
