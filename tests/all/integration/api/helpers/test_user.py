import unittest
from app import current_app as app
from tests.all.integration.auth_helper import create_user
from app.api.helpers.user import modify_email_for_user_to_be_deleted, \
     modify_email_for_user_to_be_restored
from app.api.helpers.db import save_to_db
from app.api.helpers.exceptions import ForbiddenException

from tests.all.integration.utils import OpenEventTestCase
from tests.all.integration.setup_database import Setup


class TestUserUtilitiesHelper(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_modify_email_for_user_to_be_deleted(self):
        """Method to test modification of email for user to be deleted"""

        with app.test_request_context():
            user = create_user(email="test_user@gmail.com", password="testpass")
            save_to_db(user)
            modified_user = modify_email_for_user_to_be_deleted(user)
            self.assertEqual("test_user@gmail.com.deleted", modified_user.email)

    def test_modify_email_for_user_to_be_restored(self):
        """Method to test modification of email for user to be restored"""

        with app.test_request_context():
            user = create_user(email="test_user@gmail.com.deleted", password="testpass")
            save_to_db(user)
            modified_user = modify_email_for_user_to_be_restored(user)
            self.assertEqual("test_user@gmail.com", modified_user.email)

            user1 = create_user(email="test_user@gmail.com", password="testpass")
            save_to_db(user1)
            user2 = create_user(email="test_user@gmail.com.deleted", password="testpass")
            save_to_db(user2)
            self.assertRaises(ForbiddenException, modify_email_for_user_to_be_restored, user2)


if __name__ == '__main__':
    unittest.main()
