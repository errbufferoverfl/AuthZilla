import unittest


class TestUserController(unittest.TestCase):

    def test_create_new_user(self):
        """
        Test creation of a new user
        """
        self.assertEqual(True, False)  # add assertion here

    def test_create_new_duplicate_user(self):
        """
         Test creation of a new user with the same username
        """
        pass

    def test_get_my_user(self):
        """
        Test fetching information about logged in user

        :return:
        """
        pass

    def test_get_another_user(self):
        """
        Test fetching information about another user

        :return:
        """
        pass

    def test_delete_my_user(self):
        """
        Test deleting my user

        :return:
        """
        pass

    def test_delete_another_user(self):
        """
        Test deleting another user

        :return:
        """
        pass

    def test_delete_duplicate_user(self):
        """
        Test deleting my user twice

        :return:
        """
        pass


if __name__ == '__main__':
    unittest.main()
