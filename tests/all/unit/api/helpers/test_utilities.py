import unittest
import string
import datetime


from app.api.helpers.exceptions import UnprocessableEntity
from app.api.helpers.utilities import get_filename_from_cd
from app.api.helpers.utilities import string_empty, dasherize, represents_int, str_generator, \
                                      require_relationship, monthdelta


class TestUtilitiesHelperValidation(unittest.TestCase):
    def test_get_filename_from_cd(self):
        """Test the method get_filename_from_cd"""

        test_data_first = 'attachment; filename="image.png"'
        test_data_none = None
        expected_response_first = ('"image', '.png"')
        expected_response_none = ('', '')

        response_first = get_filename_from_cd(test_data_first)
        response_none = get_filename_from_cd(test_data_none)

        self.assertEqual(expected_response_first, response_first)
        self.assertEqual(expected_response_none, response_none)

    def test_dasherize(self):
        """Method to test whether an attribute dasherizes or not"""

        field = "starts_at"
        dasherized_field = "starts-at"
        result = dasherize(field)
        self.assertEqual(result, dasherized_field)

    def test_represents_int(self):
        """Method to test representation of int"""

        self.assertTrue(represents_int(4))
        self.assertFalse(represents_int('test'))


    def test_string_empty(self):
        """Method to test whether an empty string is correctly identified."""

        self.assertTrue(string_empty(''))
        self.assertTrue(string_empty(' '))
        self.assertTrue(string_empty('\t'))
        self.assertTrue(string_empty('\n'))
        self.assertFalse(string_empty(None))
        self.assertFalse(string_empty('some value'))
        self.assertFalse(string_empty('  some   value '))
        self.assertFalse(string_empty(0))
        self.assertFalse(string_empty([]))
        self.assertFalse(string_empty(False))

    def test_str_generator(self):
        """Method to test str_generator."""

        generated_string = str_generator()
        self.assertEqual(len(generated_string), 6)
        self.assertRegex(generated_string, r'^[A-Z0-9]+$')
        self.assertNotRegex(generated_string, r'^[a-z]+$')

        generated_string = str_generator(8, chars=string.ascii_lowercase)
        self.assertEqual(len(generated_string), 8)
        self.assertRegex(generated_string, r'^[a-z]+$')
        self.assertNotRegex(generated_string, r'^[A-Z0-9]+$')

        generated_string = str_generator(chars='ABC253')
        self.assertRegex(generated_string, r'^[ABC253]+$')

    def test_require_relationship(self):
        """Method to test relationship in request data"""

        with self.assertRaises(UnprocessableEntity):
            data = ['event']
            require_relationship(['sponsor', 'event'], data)

    def test_monthdelta(self):
        """Method to test difference in months result"""

        test_date = datetime.datetime(2000, 6, 18)
        test_future_date = monthdelta(test_date, 3)
        self.assertEqual(test_future_date, datetime.datetime(2000, 9, 18))


class TestSafeRemoteRequest(unittest.TestCase):
    """Redirects of user supplied URLs must not lead to internal services"""

    @staticmethod
    def response(status, location=None):
        from unittest.mock import MagicMock
        resp = MagicMock()
        resp.is_redirect = location is not None
        resp.headers = {'Location': location} if location else {}
        resp.status_code = status
        return resp

    def test_rejects_internal_redirect_targets(self):
        from unittest.mock import patch
        from app.api.helpers.utilities import safe_remote_request

        with patch('app.api.helpers.utilities.validate_remote_url') as validate, \
                patch('app.api.helpers.utilities.requests.request') as request:
            request.return_value = self.response(302, 'http://169.254.169.254/latest/meta-data/')
            validate.side_effect = [None, ValueError('Invalid image URL')]
            with self.assertRaises(ValueError):
                safe_remote_request('GET', 'https://example.com/image.png')
            self.assertEqual(request.call_count, 1)  # the internal target was never requested

    def test_follows_valid_redirects(self):
        from unittest.mock import patch
        from app.api.helpers.utilities import safe_remote_request

        final = self.response(200)
        with patch('app.api.helpers.utilities.validate_remote_url'), \
                patch('app.api.helpers.utilities.requests.request') as request:
            request.side_effect = [self.response(301, '/moved.png'), final]
            self.assertIs(safe_remote_request('GET', 'https://example.com/image.png'), final)
            self.assertEqual(request.call_args[0][1], 'https://example.com/moved.png')

    def test_limits_redirects(self):
        from unittest.mock import patch
        from app.api.helpers.utilities import safe_remote_request

        with patch('app.api.helpers.utilities.validate_remote_url'), \
                patch('app.api.helpers.utilities.requests.request') as request:
            request.return_value = self.response(302, 'https://example.com/loop')
            with self.assertRaises(ValueError):
                safe_remote_request('GET', 'https://example.com/loop', max_redirects=3)
            self.assertEqual(request.call_count, 4)


if __name__ == '__main__':
    unittest.main()
