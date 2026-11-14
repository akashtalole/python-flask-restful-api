import base64
import unittest

from app import current_app as app
from tests.all.integration.auth_helper import create_super_admin
from tests.all.integration.setup_database import Setup
from tests.all.integration.utils import OpenEventTestCase


class TestHealthAndEnvironment(OpenEventTestCase):
    def setUp(self):
        self.client = Setup.create_app()

    def test_health_check_is_registered(self):
        resp = self.client.get('/health-check')
        # celery has no worker in the test environment, so the check may report failure,
        # but the endpoint must exist and answer with the check results
        self.assertIn(resp.status_code, (200, 500))
        body = resp.get_json()
        self.assertIn('results', body)
        names = {result['checker'] for result in body['results']}
        self.assertIn('health_check_db', names)
        db_result = [r for r in body['results'] if r['checker'] == 'health_check_db'][0]
        self.assertTrue(db_result['passed'])

    def test_environment_requires_admin_and_hides_process_environ(self):
        self.assertEqual(self.client.get('/environment').status_code, 401)

        with app.test_request_context():
            create_super_admin('admin@example.com', 'password')
        credentials = base64.b64encode(b'admin@example.com:password').decode()
        resp = self.client.get('/environment', headers={'Authorization': 'Basic ' + credentials})
        self.assertEqual(resp.status_code, 200, resp.get_data(as_text=True))
        data = resp.get_json()
        self.assertIn('python', data)
        self.assertNotIn('process', data)


if __name__ == '__main__':
    unittest.main()
