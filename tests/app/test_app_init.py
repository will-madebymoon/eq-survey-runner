import unittest
from app.setup import get_asset

class TestAppInit(unittest.TestCase):

    def test_get_asset_defaults_to_minified(self):
        self.assertEqual('some.min.css', get_asset('some.css'))
        self.assertEqual('some.min.js', get_asset('some.js'))

    def test_get_asset_can_get_full_fat_asset(self):
        self.assertEqual('some.css', get_asset('some.css', minified=False))
        self.assertEqual('some.js', get_asset('some.js', minified=False))


if __name__ == '__main__':
    unittest.main()
