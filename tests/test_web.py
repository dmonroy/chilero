from aiohttp import request
from chilero import web
from chilero.web.test import WebTestCase, asynctest


class HelloView(web.View):

    def get(self):
        return web.Response('Hello world!')


class MultiView(web.View):

    def get(self, type):

        types = dict(
            octet_stream=lambda: web.Response('Hello world!'),
            plain=lambda: web.Response('Hello world!', content_type='text/plain'),
            html=lambda: web.HTMLResponse('<h1>Hello world!</h1>'),
            json=lambda: web.JSONResponse(dict(hello='world!')),
            javascript=lambda: web.JavaScriptResponse('// hello world!'),
        )

        return types.get(type, 'plain')()


class TestWeb(WebTestCase):
    routes = [
        ['/hello/', HelloView],
        ['/{type}', MultiView]
    ]

    @asynctest
    def test_hello_view(self):

        resp = yield from request(
            'GET',self.full_url('/hello'),loop=self.loop
        )
        self.assertEqual(resp.status, 200)


    @asynctest
    def test_multi_view(self):

        types = dict(
            octet_stream=['application/octet-stream', 'Hello world!'],
            plain=['text/plain', 'Hello world!'],
            html=['text/html', '<h1>Hello world!</h1>'],
            javascript=['application/javascript', '// hello world!'],
            json=['application/json', '{"hello": "world!"}']
        )

        for t in types.keys():
            resp = yield from request(
                'GET',
                self.full_url(self.app.reverse('multiview', type=t)),
                loop=self.loop
            )

            self.assertEqual(resp.status, 200)

            self.assertEqual(
                types[t][0], resp.headers.get('CONTENT-TYPE'))

            text = yield from resp.text()

            # self.assertEqual(types[t][1], text)
