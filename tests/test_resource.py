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

veggies = dict(
    cucumber=dict(
        colors=['green']
    ),
    beet=dict(
        colors=['purple']
    ),
)


class ViewBasedStats(web.View):
    def get(self):
        return web.JSONResponse(
            dict(
                count=fruits.__len__()
            )
        )


class GlobalStatsResource(web.Resource):
    def index(self):
        return self.response(
            dict(
                count=fruits.__len__()
            )
        )


class SingleStatsResource(web.Resource):
    def default_kwargs_for_urls(self):
        return dict(
            fruit_id=self.request.match_info['fruit_id']
        )

    def index(self, fruit_id):
        return self.response(
            dict(
                count=fruits[fruit_id]['colors'].__len__()
            )
        )


class FruitResource(web.Resource):
    resource_name = 'fruit'

    nested_collection_resources = dict(
        stats=GlobalStatsResource,
        stats2=ViewBasedStats
    )
    nested_entity_resources = dict(
        stats=SingleStatsResource
    )

    definition = dict(
        description='A long description of the resource'
    )

    def index(self):
        response = dict(
            fruits=fruits
        )
        return self.response(response)

    def show(self, id):
        if id not in fruits:
            raise HTTPNotFound()

        return self.response(fruits[id])

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


class VeggiesResource(web.Resource):
    resource_name = 'veggies'

    def get_definition(self):
        return dict(
            description='A HTTP resource of veggies'
        )

    def index(self):
        response = dict(
            veggies=veggies
        )
        return self.response(response)

    def show(self, id):
        if id not in veggies:
            raise HTTPNotFound()

        return self.response(veggies[id])


class TestResource(WebTestCase):
    routes = [
        ['/fruit', FruitResource],
        ['/veggies', VeggiesResource]
    ]

    @asynctest
    def test_definition_from_property(self):
        resp = yield from self.sess.get(
            self.full_url(self.app.reverse('fruit_definition'))
        )

        self.assertEqual(resp.status, 200)
        jr = yield from resp.json()

        self.assertEqual(jr['description'], 'A long description of the resource')
        resp.close()

    @asynctest
    def test_definition_from_method(self):
        resp = yield from self.sess.get(
            self.full_url(self.app.reverse('veggies_definition'))
        )

        self.assertEqual(resp.status, 200)
        jr = yield from resp.json()

        self.assertEqual(jr['description'], 'A HTTP resource of veggies')
        resp.close()

    @asynctest
    def test_index(self):
        resp = yield from self.sess.get(
            self.full_url(self.app.reverse('fruit_index'))
        )

        self.assertEqual(resp.status, 200)
        jr = yield from resp.json()
        self.assertEqual(jr['fruits'], fruits)
        self.assertTrue(jr['self'].endswith('/fruit'))
        resp.close()


    @asynctest
    def test_show(self):
        resp = yield from self.sess.get(
            self.full_url(self.app.reverse('fruit_item', id='orange'))
        )

        self.assertEqual(resp.status, 200)
        jr = yield from resp.json()

        self.assertEqual(jr['body'], dict(colors=['orange', 'yellow', 'green']))
        resp.close()

        self.assertTrue(jr['self'].endswith('/fruit/orange'))

        resp2 = yield from self.sess.get(
            self.full_url(self.app.reverse('fruit_item', id='mango'))
        )

        self.assertEqual(resp2.status, 404)
        resp2.close()

    @asynctest
    def test_new(self):

        resp = yield from self.sess.post(
            self.full_url(self.app.reverse('fruit_index')),
            data=json.dumps(dict(name='apple', colors=['red', 'green'])),
        )

        self.assertEqual(resp.status, 200)

        resp.close()
        resp = yield from self.sess.get(
            self.full_url(self.app.reverse('fruit_item', id='apple'))
        )

        self.assertEqual(resp.status, 200)
        jr = yield from resp.json()
        self.assertEqual(jr['body'], dict(colors=['red', 'green']))
        resp.close()

    @asynctest
    def test_update(self):

        resp = yield from self.sess.post(
            self.full_url(self.app.reverse('fruit_index')),
            data=json.dumps(dict(name='pear', colors=['green'])),
        )

        self.assertEqual(resp.status, 200)
        resp.close()

        resp = yield from self.sess.get(
            self.full_url(self.app.reverse('fruit_item', id='pear'))
        )

        self.assertEqual(resp.status, 200)
        jr = yield from resp.json()
        self.assertEqual(jr['body'], dict(colors=['green']))
        resp.close()

        resp = yield from self.sess.put(
            self.full_url(self.app.reverse('fruit_item', id='pear')),
            data=json.dumps(dict(colors=['green', 'yellow'])),
        )

        self.assertEqual(resp.status, 200)
        resp.close()

        resp = yield from self.sess.get(
            self.full_url(self.app.reverse('fruit_item', id='pear'))
        )

        self.assertEqual(resp.status, 200)
        jr = yield from resp.json()
        self.assertEqual(jr['body'], dict(colors=['green', 'yellow']))
        resp.close()

    @asynctest
    def test_delete(self):

        resp = yield from self.sess.post(
            self.full_url(self.app.reverse('fruit_index')),
            data=json.dumps(dict(name='grape', colors=['purple'])),
        )

        self.assertEqual(resp.status, 200)
        resp.close()

        resp = yield from self.sess.get(
            self.full_url(self.app.reverse('fruit_item', id='grape'))
        )

        self.assertEqual(resp.status, 200)
        jr = yield from resp.json()

        self.assertEqual(jr['body'], dict(colors=['purple']))
        resp.close()

        resp = yield from self.sess.delete(
            self.full_url(self.app.reverse('fruit_item', id='grape'))
        )

        self.assertEqual(resp.status, 200)
        resp.close()

        resp = yield from self.sess.get(
            self.full_url(self.app.reverse('fruit_item', id='grape'))
        )

        self.assertEqual(resp.status, 404)
        resp.close()

    @asynctest
    def test_parent_url(self):
        resp = yield from self.sess.get(
            self.full_url(
                self.app.reverse('singlestatsresource_index', fruit_id='orange')
            )
        )

        j = yield from resp.json()
        resp.close()
        assert j['parent'].endswith('/fruit/orange')

        resp2 = yield from self.sess.get(
            self.full_url(
                self.app.reverse('globalstatsresource_index')
            )
        )
        j2 = yield from resp2.json()
        resp2.close()
        assert j2['parent'].endswith('/fruit')

        resp2 = yield from self.sess.get(
            self.full_url(
                self.app.reverse('viewbasedstats')
            )
        )
        j2 = yield from resp2.json()
        resp2.close()
        assert j2['count'] == 3
