import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.parser import parse_key_value

class TestParser(unittest.TestCase):
    def test_basic_parse(self):
        text = "host=localhost\nport=8080\n# comment\n"
        expected = {"host": "localhost", "port": "8080"}
        self.assertEqual(parse_key_value(text), expected)

if __name__ == '__main__':
    unittest.main()
