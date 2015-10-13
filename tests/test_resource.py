import aiohttp
from aiohttp.web_exceptions import HTTPNotFound
import json
from chilero import web
from chilero.web.test import WebTestCase, asynctest

fruits = dict(
    orange=dict(
        colors=['orange', 'yellow', 'green']
    ),
    strawberry=dict(
        colors=['red', 'pink']
    ),
)

class FruitResource(web.Resource):

    def index(self):
        return web.JSONResponse(fruits)

    def show(self, id):
        if id not in fruits:
            raise HTTPNotFound()

        return web.JSONResponse(fruits[id])

    def new(self):
        data = yield from self.request.json()
        fruits[data['name']] = dict(colors=data['colors'])

        return web.JSONResponse(fruits[data['name']])

    def update(self, id):
        data = yield from self.request.json()
        fruits[id] = dict(colors=data['colors'])

        return web.JSONResponse(fruits[id])

    def destroy(self, id):
        fruits.pop(id)
        return web.JSONResponse(None)


class TestResource(WebTestCase):
    routes = [
        ['/fruit', FruitResource]
    ]

    @asynctest
    def test_index(self):
        resp = yield from aiohttp.get(self.full_url('/fruit'))

        self.assertEqual(resp.status, 200)
        jr = yield from resp.json()
        self.assertEqual(set(jr.keys()), {'orange', 'strawberry'})

        resp.close()

    @asynctest
    def test_show(self):
        resp = yield from aiohttp.get(self.full_url('/fruit/orange'))

        self.assertEqual(resp.status, 200)
        jr = yield from resp.json()
        self.assertEqual(jr, dict(colors=['orange', 'yellow', 'green']))
        resp.close()

        resp2 = yield from aiohttp.get(self.full_url('/fruit/mango'))

        self.assertEqual(resp2.status, 404)
        resp2.close()

    @asynctest
    def test_new(self):

        resp = yield from aiohttp.post(
            self.full_url('/fruit'),
            data=json.dumps(dict(name='apple', colors=['red', 'green'])),
        )

        self.assertEqual(resp.status, 200)

        resp.close()
        resp = yield from aiohttp.get(self.full_url('/fruit/apple'))

        self.assertEqual(resp.status, 200)
        jr = yield from resp.json()
        self.assertEqual(jr, dict(colors=['red', 'green']))
        resp.close()

    @asynctest
    def test_update(self):

        resp = yield from aiohttp.post(
            self.full_url('/fruit'),
            data=json.dumps(dict(name='pear', colors=['green'])),
        )

        self.assertEqual(resp.status, 200)
        resp.close()

        resp = yield from aiohttp.get(self.full_url('/fruit/pear'))

        self.assertEqual(resp.status, 200)
        jr = yield from resp.json()
        self.assertEqual(jr, dict(colors=['green']))
        resp.close()

        resp = yield from aiohttp.put(
            self.full_url('/fruit/pear'),
            data=json.dumps(dict(colors=['green', 'yellow'])),
        )

        self.assertEqual(resp.status, 200)
        resp.close()

        resp = yield from aiohttp.get(self.full_url('/fruit/pear'))

        self.assertEqual(resp.status, 200)
        jr = yield from resp.json()
        self.assertEqual(jr, dict(colors=['green', 'yellow']))
        resp.close()

    @asynctest
    def test_delete(self):

        resp = yield from aiohttp.post(
            self.full_url('/fruit'),
            data=json.dumps(dict(name='grape', colors=['purple'])),
        )

        self.assertEqual(resp.status, 200)
        resp.close()

        resp = yield from aiohttp.get(self.full_url('/fruit/grape'))

        self.assertEqual(resp.status, 200)
        jr = yield from resp.json()
        self.assertEqual(jr, dict(colors=['purple']))
        resp.close()

        resp = yield from aiohttp.delete(self.full_url('/fruit/grape'))

        self.assertEqual(resp.status, 200)
        resp.close()

        resp = yield from aiohttp.get(self.full_url('/fruit/grape'))

        self.assertEqual(resp.status, 404)
        resp.close()



