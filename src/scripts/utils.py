import sys
import yaml
from pathlib import Path

def error(message: str):
    """Prints an error message to stderr and exits."""
    sys.stderr.write(f"ERROR: {message}\n")
    sys.exit(1)

def warning(message: str):
    """Prints an warning message to stderr."""
    sys.stderr.write(f"WARNING: {message}\n")

def info(message: str):
    """Prints an info message to stderr."""
    sys.stderr.write(f"INFO: {message}\n")

def replace_x(x: str, new_value: str, in_str: str) -> str:
    """Replaces `x` with the given `new_value` in a string `in_str`."""
    return in_str.replace(x, new_value)

def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text())

