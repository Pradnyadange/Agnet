from sample_pkg.core import parse_config

def test_parse_config():
    data = parse_config('title = "sample_test"\ncount = 42\n')
    assert data["title"] == "sample_test"
    assert data["count"] == 42
