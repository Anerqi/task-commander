from src.parser import parse_record

def test_parse_record():
    assert parse_record('  HELLO  ') == 'hello'
