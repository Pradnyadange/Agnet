"""Test that load_config correctly reads a TOML file via text-mode handle."""
import os
import tempfile
import sys
import pathlib

# Make breaking_pkg importable whether pytest is run from the fixture dir or from the project root
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from breaking_pkg.loader import load_config


def test_load_config_reads_toml_file():
    """This test exercises load_config with a text-mode file handle.
    It passes with 'toml' (text-mode OK) but FAILS with 'tomllib as toml'
    because tomllib.load() requires binary mode.
    """
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".toml", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write('[section]\nkey = "value"\ncount = 7\n')
        tmp_path = tmp.name

    try:
        data = load_config(tmp_path)
        assert data["section"]["key"] == "value"
        assert data["section"]["count"] == 7
    finally:
        os.unlink(tmp_path)
