import os
import sys
import yaml
import logger
from datetime import datetime
from pathlib import Path

def now() -> datetime:
    return datetime.now()

def now_str(fmt: str = '%Y-%m-%d_%H-%M-%S') -> str:
    return now().strftime(fmt)

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

def get_default_log_file(script_name: str) -> str:
    dir = f'logs/{now_str()}'
    return f'{log_dir}/{script}.log'

def make_logger(log_file: str, name: str = '__name__', level: int = logging.INFO) -> logging.Logger:
    make_parent_dirs(log_file)
    logging.basicConfig(filename=log_file, level=level)
    logger = logging.getLogger(name)
    logger.set_level(level)
    return logger

def make_parent_dirs(file: str, , exist_ok: bool = True) -> Path:
    path = Path(file)
    if file == path.name:  # no path prefix
        return Path('.')
    else:
        dirs = path.parent
        os.makedirs(dirs, exist_ok=exist_ok)
        return dirs

def ensure_dirs_exist(dirs: list[str], logger: logger.Logger):
    missing_dirs=()
    for dir in dirs:
        missing_dirs.append(dir) if not os.path.isdir(dir)
    if len(missing_dirs) > 0:
        logger.error(f"These directories don't exit: {missing_dirs}")
        sys.exit(1)

def not_null(value, message: str):
    if not value:
    self.logger.error(message)
    sys.exit(1)
    
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
