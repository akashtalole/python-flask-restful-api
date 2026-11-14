import base64
import json
import unittest

from itsdangerous import Serializer

from app import current_app as app
from app.api.helpers.db import save_to_db
from app.api.helpers.utilities import get_serializer
from app.models.user import User
from tests.all.integration.auth_helper import create_user
from tests.all.integration.setup_database import Setup
from tests.all.integration.utils import OpenEventTestCase


def post_json(client, url, payload, headers=None):
    return client.post(url, data=json.dumps(payload), content_type='application/json', headers=headers or {})


class TestAuthFlow(OpenEventTestCase):
    """End to end checks of login, token handling and e-mail verification over HTTP"""

    def setUp(self):
        self.client = Setup.create_app()

    def login(self, email='flow@example.com', password='password', **extra):
        payload = {'email': email, 'password': password}
        payload.update(extra)
        return post_json(self.client, '/v1/auth/login', payload)

    def make_user(self, **kwargs):
        with app.test_request_context():
            user = create_user('flow@example.com', 'password', **kwargs)
            return user.id

    def test_login_and_protected_endpoint(self):
        user_id = self.make_user(is_verified=True)
        resp = self.login()
        self.assertEqual(resp.status_code, 200, resp.get_data(as_text=True))
        token = resp.get_json()['access_token']
        url = '/v1/users/%d' % user_id

        # authenticated request works
        resp = self.client.get(url, headers={'Authorization': 'JWT ' + token})
        self.assertEqual(resp.status_code, 200, resp.get_data(as_text=True))
        self.assertEqual(resp.get_json()['data']['attributes']['email'], 'flow@example.com')

        # without a token it is rejected
        resp = self.client.get(url)
        self.assertIn(resp.status_code, (401, 403))

        # a token that was not signed by us is rejected
        resp = self.client.get(url, headers={'Authorization': 'JWT ' + token[:-4] + 'abcd'})
        self.assertIn(resp.status_code, (401, 422))

    def test_login_with_wrong_password(self):
        self.make_user(is_verified=True)
        resp = self.login(password='wrong')
        self.assertEqual(resp.status_code, 401)

    def test_refresh_token(self):
        self.make_user(is_verified=True)
        resp = self.login(**{'remember-me': True, 'include-in-response': True})
        self.assertEqual(resp.status_code, 200, resp.get_data(as_text=True))
        data = resp.get_json()
        self.assertIn('refresh_token', data)

        # an access token cannot be used to refresh
        resp = post_json(self.client, '/v1/auth/token/refresh', {},
                         headers={'Authorization': 'JWT ' + data['access_token']})
        self.assertIn(resp.status_code, (401, 422))

        resp = post_json(self.client, '/v1/auth/token/refresh', {},
                         headers={'Authorization': 'JWT ' + data['refresh_token']})
        self.assertEqual(resp.status_code, 200, resp.get_data(as_text=True))
        self.assertIn('access_token', resp.get_json())

    def test_email_verification_rejects_forged_tokens(self):
        """Tokens signed with the old, publicly known key must not verify an account"""
        self.make_user(is_verified=False)
        forged = Serializer('secret_key').dumps(['flow@example.com', 'ABC123'])
        encoded = base64.b64encode(forged.encode() if isinstance(forged, str) else forged).decode()
        resp = post_json(self.client, '/v1/auth/verify-email', {'data': {'token': encoded}})
        self.assertEqual(resp.status_code, 400)
        with app.test_request_context():
            self.assertFalse(User.query.filter_by(email='flow@example.com').one().is_verified)

    def test_email_verification_accepts_genuine_tokens(self):
        self.make_user(is_verified=False)
        with app.test_request_context():
            genuine = get_serializer().dumps(['flow@example.com', 'ABC123'])
        encoded = base64.b64encode(genuine.encode() if isinstance(genuine, str) else genuine).decode()
        resp = post_json(self.client, '/v1/auth/verify-email', {'data': {'token': encoded}})
        self.assertEqual(resp.status_code, 200, resp.get_data(as_text=True))
        with app.test_request_context():
            self.assertTrue(User.query.filter_by(email='flow@example.com').one().is_verified)

    def test_change_password_requires_fresh_token(self):
        self.make_user(is_verified=True)
        resp = self.login(**{'remember-me': True, 'include-in-response': True})
        refresh_access = post_json(self.client, '/v1/auth/token/refresh', {},
                                   headers={'Authorization': 'JWT ' + resp.get_json()['refresh_token']})
        stale = refresh_access.get_json()['access_token']  # not fresh
        payload = {'data': {'old-password': 'password', 'new-password': 'new-password-1'}}
        resp = post_json(self.client, '/v1/auth/change-password', payload, headers={'Authorization': 'JWT ' + stale})
        self.assertIn(resp.status_code, (401, 422))


if __name__ == '__main__':
    unittest.main()
