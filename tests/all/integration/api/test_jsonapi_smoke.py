import json
import unittest

from app import current_app as app
from tests.all.integration.auth_helper import create_super_admin
from tests.all.integration.setup_database import Setup
from tests.all.integration.utils import OpenEventTestCase

JSONAPI = 'application/vnd.api+json'


class TestJsonApiSmoke(OpenEventTestCase):
    """Create / read / filter / update / delete through the JSON:API layer"""

    def setUp(self):
        self.client = Setup.create_app()
        with app.test_request_context():
            create_super_admin('admin@example.com', 'password')
        resp = self.client.post('/v1/auth/login', data=json.dumps({'email': 'admin@example.com',
                                                                   'password': 'password'}),
                                content_type='application/json')
        self.assertEqual(resp.status_code, 200, resp.get_data(as_text=True))
        self.headers = {'Authorization': 'JWT ' + resp.get_json()['access_token'], 'Accept': JSONAPI}

    def request(self, method, url, payload=None):
        kwargs = {'headers': self.headers}
        if payload is not None:
            kwargs.update(data=json.dumps(payload), content_type=JSONAPI)
        return getattr(self.client, method)(url, **kwargs)

    def event_payload(self, name):
        return {'data': {'type': 'event', 'attributes': {
            'name': name, 'starts-at': '2099-05-30T09:30:00+00:00', 'ends-at': '2099-06-01T17:00:00+00:00',
            'timezone': 'UTC'}}}

    def test_event_lifecycle(self):
        resp = self.request('post', '/v1/events', self.event_payload('First event'))
        self.assertEqual(resp.status_code, 201, resp.get_data(as_text=True))
        event = resp.get_json()['data']
        event_id = event['id']
        self.assertEqual(event['attributes']['name'], 'First event')
        self.assertEqual(event['type'], 'event')

        resp = self.request('post', '/v1/events', self.event_payload('Second event'))
        self.assertEqual(resp.status_code, 201, resp.get_data(as_text=True))

        # list, pagination, sorting and filtering
        resp = self.request('get', '/v1/events?sort=name&page[size]=1')
        self.assertEqual(resp.status_code, 200, resp.get_data(as_text=True))
        body = resp.get_json()
        self.assertEqual(len(body['data']), 1)
        self.assertEqual(body['data'][0]['attributes']['name'], 'First event')
        self.assertEqual(body['meta']['count'], 2)

        flt = json.dumps([{'name': 'name', 'op': 'eq', 'val': 'Second event'}])
        resp = self.request('get', '/v1/events?filter=' + flt)
        self.assertEqual(resp.status_code, 200, resp.get_data(as_text=True))
        self.assertEqual([e['attributes']['name'] for e in resp.get_json()['data']], ['Second event'])

        # detail + update
        resp = self.request('get', '/v1/events/%s' % event_id)
        self.assertEqual(resp.status_code, 200, resp.get_data(as_text=True))

        patch = {'data': {'type': 'event', 'id': event_id, 'attributes': {'name': 'Renamed event'}}}
        resp = self.request('patch', '/v1/events/%s' % event_id, patch)
        self.assertEqual(resp.status_code, 200, resp.get_data(as_text=True))
        self.assertEqual(resp.get_json()['data']['attributes']['name'], 'Renamed event')

        # unknown resource
        self.assertEqual(self.request('get', '/v1/events/99999').status_code, 404)

        # delete (events are soft deleted)
        resp = self.request('delete', '/v1/events/%s' % event_id)
        self.assertEqual(resp.status_code, 200, resp.get_data(as_text=True))
        self.assertEqual(self.request('get', '/v1/events/%s' % event_id).status_code, 404)

    def test_invalid_payload_is_rejected(self):
        resp = self.request('post', '/v1/events', {'data': {'type': 'event', 'attributes': {'name': 'No dates'}}})
        self.assertIn(resp.status_code, (400, 422), resp.get_data(as_text=True))

    def test_anonymous_cannot_create_events(self):
        resp = self.client.post('/v1/events', data=json.dumps(self.event_payload('Nope')), content_type=JSONAPI)
        self.assertIn(resp.status_code, (401, 403))


if __name__ == '__main__':
    unittest.main()
