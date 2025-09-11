import os
import sys
import yaml
from pathlib import Path

def log(label: str, message: str, files=[]):
    """Logs a message to stderr and optionally also any files specified."""
    msg = f"{label}: {message}\n"
    sys.stderr.write(msg)
    for file in files:
        file.write(msg)

def error(message: str, files=[]):
    """Prints an error message to stderr and optionally also any files specified, then exits."""
    log("ERROR", message, files)
    sys.exit(1)

def warning(message: str, files=[]):
    """Prints an warning message to stderr and optionally also any files specified."""
    log("WARNING", message, files)

def info(message: str, files=[]):
    """Prints an info message to stderr and optionally also any files specified."""
    log("INFO", message, files)

def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text())

def model_dir_name(model: str) -> str:
    """Replace colon with underscore in the model name."""
    return model.replace(":", "_")

def use_cases() -> dict:
    """Return a dictionary with the use case names as keys 
    and the corresponding labels as values."""
    return {
        "prescription refills": "refill",
        "non prescription refills": "other",
        "emergency": "emergency",
    }

def ensure_dir_exists(dir: str, label="", files=[]):
    if not os.path.isdir(dir):
        lbl = "" if len(label) == 0 else " "+label
        error(f"The{lbl} directory {dir} doesn't exit!", files=files)

def make_full_prompt(prompt: str, system_prompt: dict) -> str:
    return f"""
SYSTEM PROMPT: 
{system_prompt}

PROMPT: 
{prompt}
"""

def extract_content(litellm_reponse) -> str:
    response_dict = litellm_reponse.to_dict()
    # TODO: There must be an easier way to get the "content"!!!
    return response_dict['choices'][0]['message']['content']
