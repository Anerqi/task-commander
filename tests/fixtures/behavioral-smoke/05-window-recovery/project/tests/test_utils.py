import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils import slugify

class TestUtils(unittest.TestCase):
    def test_slugify(self):
        self.assertEqual(slugify("Hello World!"), "hello-world")

if __name__ == '__main__':
    unittest.main()
