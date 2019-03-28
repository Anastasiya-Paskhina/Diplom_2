import unittest
from vk_app.users_classes import MainUser
from VKinder import top10


class MyTest(unittest.TestCase):
    def test_top10(self):
        main_user = MainUser('8517264')
        main_user.select_user_info()
        main_user.groups()
        main_user.friends()
        self.assertIsInstance(top10(main_user)[0], dict)


if __name__ == '__main__':
    unittest.main()