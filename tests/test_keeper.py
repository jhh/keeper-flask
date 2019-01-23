import unittest

import keeper


class KeeperTestCase(unittest.TestCase):

    def setUp(self):
        self.app = keeper.server.test_client()

    def test_index(self):
        rv = self.server.get('/')
        self.assertIn('Stryke Force Keeper', rv.data.decode())


if __name__ == '__main__':
    unittest.main()
