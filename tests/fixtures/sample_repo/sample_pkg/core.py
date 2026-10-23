import toml

def parse_config(raw_string: str) -> dict:
    """Parse configuration data using toml."""
    return toml.loads(raw_string)
