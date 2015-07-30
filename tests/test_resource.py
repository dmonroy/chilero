from aiohttp import request
from aiohttp.web_exceptions import HTTPNotFound
from dmonroy import web
from dmonroy.web.test import WebTestCase, asynctest


class FruitResource(web.Resource):
    fruits = dict(
        orange=dict(
            colors=['orange', 'yellow', 'green']
        ),
        strawberry=dict(
            colors=['red', 'pink']
        ),
    )

    def index(self):
        return web.JSONResponse(self.fruits)

    def show(self, id):
        if id not in self.fruits:
            raise HTTPNotFound()

        return web.JSONResponse(self.fruits[id])

    def new(self):
        return web.JSONResponse(
            dict()
        )

    def update(self):
        return web.JSONResponse(
            dict()
        )


class TestWeb(WebTestCase):
    routes = [
        ['/fruit', FruitResource]
    ]

    @asynctest
    def test_index(self):
        resp = yield from request(
            'GET', self.full_url('/fruit'), loop=self.loop
        )

        self.assertEqual(resp.status, 200)

    @asynctest
    def test_show(self):
        resp = yield from request(
            'GET', self.full_url('/fruit/orange'), loop=self.loop
        )

        self.assertEqual(resp.status, 200)

        resp2 = yield from request(
            'GET', self.full_url('/fruit/mango'), loop=self.loop
        )

        self.assertEqual(resp2.status, 404)
