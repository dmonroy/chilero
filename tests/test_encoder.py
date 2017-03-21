import json
import datetime

from chilero import web
from chilero.web import JSONResponse
from chilero.web.test import WebTestCase, asynctest

import aiohttp


class DateEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (datetime.date, datetime.date)):
            return o.isoformat()

        return super(DateEncoder, self).default(o)

class DateEncoderView(web.View):
    def get(self):
        return JSONResponse(
            dict(
                today=datetime.date.today()
            ),
            cls=DateEncoder
        )

class DateEncoderResource(web.Resource):
    encoder_class = DateEncoder

    def index(self):
        return self.response(
            dict(
                today=datetime.date.today()
            )
        )

class TestEncoder(WebTestCase):
    routes = [
        ['/resource', DateEncoderResource],
        ['/view', DateEncoderView]
    ]

    @asynctest
    def test_resource(self):
        resp = yield from self.sess.get(self.full_url('/resource'))

        self.assertEqual(resp.status, 200)
        jr = yield from resp.json()
        self.assertEqual(jr['today'], datetime.date.today().isoformat())
        resp.close()

    @asynctest
    def test_view(self):
        resp = yield from self.sess.get(self.full_url('/view'))

        self.assertEqual(resp.status, 200)
        jr = yield from resp.json()
        self.assertEqual(jr, dict(today=datetime.date.today().isoformat()))
        resp.close()
