import toml


def load_config(path: str) -> dict:
    """Load configuration from a TOML file at path (opened in text mode)."""
    with open(path, "r", encoding="utf-8") as f:
        return toml.load(f)
