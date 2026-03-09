import argparse
import json
import logging
import os
import sys
import yaml
from datetime import datetime
from importlib import metadata
from json.decoder import JSONDecodeError
from pathlib import Path
from pprint import pprint
from typing import Callable

from litellm.types.utils import ModelResponse

common_defaults = {
    "model":                        "ollama_chat/gpt-oss:20b",
    "service_url":                  "http://localhost:11434",
    "template_dir":                 "prompts/templates",
    "data_dir":                     "data",
    "levenshtein-ratio-threshold":  0.95,
}

timestamp_str_fmt  = '%Y:%m:%d %H:%M:%S'
timestamp_file_fmt = '%Y-%m-%d_%H-%M-%S'


def setup(
        tool: str, 
        description: str, 
        epilog: str = '', 
        add_arguments: Callable[[argparse.ArgumentParser], None] = None,
        omit: {str} = {}
    ) -> (argparse.Namespace, logging.Logger):
    parser = parser_with_common_args(
        tool, 
        description,
        epilog=epilog,
        omit=omit)
    if add_arguments:
        add_arguments(parser)
    args = parser.parse_args()
    logger = make_logger(args.log_file, name=tool, level=args.log_level)
    log_args(logger, tool, args, epilog=epilog)
    return args, logger

def parser_with_common_args(tool: str, description: str, epilog: str = None, omit: {str} = {}) -> argparse.ArgumentParser:
    """
    Returns an `ArgumentParser` with the default arguments and a format string 
    that can be used by the calling program to print the actual values specified
    by the user.
    """
    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    if not 'model' in omit:
        parser.add_argument("-m", "--model", default=common_defaults['model'], 
            help=f"Use MODEL. Default {common_defaults['model']}")
    if not 'service-url' in omit:
        parser.add_argument("-s", "--service-url", default=common_defaults['service_url'],
            help=f"Use SERVICE_URL as the inference hosting service URL. Default: {common_defaults['service_url']}")
    if not 'template-dir' in omit:
        parser.add_argument("-t", "--template-dir", default=common_defaults['template_dir'],
            help=f"Use TEMPLATE_DIR as the location to find the prompt templates used. Default: {common_defaults['template_dir']}")
    if not 'data-dir' in omit:
        parser.add_argument("-d", "--data-dir", default=common_defaults['data_dir'], 
            help=f"Directory where data files are read or written. Default: {common_defaults['data_dir']}")
    if not 'log-file' in omit:
        default_log_file = get_default_log_file(tool)
        default_log_level = get_default_log_level(tool)
        parser.add_argument("-l", "--log-file", default=default_log_file, 
            help=f"Where logging is written. Default: {default_log_file}.")
        parser.add_argument("--log-level", default=logging.INFO, type=int, 
            help=f"The integer value for the logging level (see https://docs.python.org/3/library/logging.html#logging-levels) is written. Default: {default_log_level} ({logging_level_to_string(default_log_level)}).")
    if not 'verbose' in omit:
        parser.add_argument("-v", "--verbose", action='store_true',
                help="Print some extra output. Useful for some testing and debugging scenarios.")
    return parser

def add_info_str(label: str, value: str, separator: str = ':') -> str:
    lbl = label + separator
    return f"  {lbl:20s} {value}"

def logging_level_to_string(level: int = -1):
    if level < 0:
        level = logger.getEffectiveLevel()
    return logging.getLevelName(level)

def log_args(logger: logging.Logger, tool: str, args: argparse.Namespace, epilog: str = None):
    ns = now_str(fmt = timestamp_str_fmt)
    logging.info(f" ({ns}) Running {tool} with these argument values:")
    for k, v in vars(args).items():
        if k == 'log_level':
            v = f"{v} (== logging.{logging_level_to_string(v)})"
        logging.info(add_info_str(k, v))

    if epilog:
        logging.info('')  
        logging.info(' '+epilog)  

def get_package_version(logger: logging.Logger) -> str | None:
    """
    Return the version string in the project's pyproject.toml. Note that we have to keep
    the name used below in sync with the name in that file: `ai-application-testing`.
    If the version information can't be determined, None is returned. This usually means that
    the project was not pip installed, i.e., `uv pip install -e .` We log this possibility.
    """
    try:
        version = metadata.version('ai-application-testing')
        if not version:
            logger.error(f"The version string returned is empty. Make sure it is defined in pyproject.toml, then run 'uv pip install -e .'")
            version = None
    except metadata.PackageNotFoundError as pnfe:
        logger.error(f"Could not determine the package version {pnfe}. Try running 'uv pip install -e .'")
        version = None
    return version

def now() -> datetime:
    return datetime.now()

def now_str(fmt: str = timestamp_str_fmt) -> str:
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

def get_default_log_file(tool_name: str) -> str:
    log_dir = f'logs/{now_str(fmt = timestamp_file_fmt)}'
    return f'{log_dir}/{tool_name}.log'

def get_default_log_level(ignored: str) -> int:
    return logging.INFO

def make_logger(log_file: str, name: str = '__name__', level: int = logging.INFO) -> logging.Logger:
    make_parent_dirs(log_file)
    logging.basicConfig(filename=log_file, level=level)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    level_str = logging.getLevelName(level)
    print(f'Logging to {log_file}, level {level_str}')    
    return logger

def make_parent_dirs(file: str, exist_ok: bool = True) -> Path:
    path = Path(file)
    if file == path.name:  # no path prefix
        return Path('.')
    else:
        dirs = path.parent
        os.makedirs(dirs, exist_ok=exist_ok)
        return dirs

def ensure_dirs_exist(*dirs):
    missing_dirs=[]
    for dir in dirs:
        if not os.path.isdir(dir):
            missing_dirs.append(dir) 
    if len(missing_dirs) > 0:
        raise ValueError(f"These directories don't exit: {', '.join(missing_dirs)}")

def make_full_prompt(prompt: str, system_prompt: any, session: [(str,str)] = []) -> str:
    ss = ["SESSION:"]
    for query, reply in session:
        ss.append(f"query: {query}")
        ss.append(f"reply: {reply}")
        ss.append('\n')

    return f"""
SYSTEM PROMPT: 
{system_prompt}

USER PROMPT: 
{prompt}

{'\n'.join(ss)}
"""

def parse_json(text: any) -> dict[str,any] | str:
    """Parse a JSON string, returning either a dictionary or an error string if parsing fails."""
    error_msg = ''
    try:
        obj = json.loads(text)
        return obj
    except (JSONDecodeError, TypeError) as err:
        error_msg = f"ERROR {err}: text not JSON? <{text}> (type: {type(text)})"
        if self.logger:
            self.logger.error(error_msg)
        return error_msg

# TODO: This is duplicated now in the HandleResponse class, which is used by
# the ChatBot app, but not by the "tools".
def extract_content(litellm_reponse: ModelResponse) -> str:
    """Returns the JSON-formatted string content we care about."""
    response_dict = litellm_reponse.to_dict()
    # TODO: There must be an easier way to get the "content"!!!
    content = response_dict['choices'][0]['message']['content']
    print(f"content (type = {type(content)}: {content})")
    return content

