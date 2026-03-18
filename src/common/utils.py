import argparse
import json
import logging
import os
import re
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
    "service-url":                  "http://localhost:11434",
    "template-dir":                 "prompts/templates",
    "data-dir":                     "data",
    "levenshtein-ratio-threshold":  0.95,
}

timestamp_str_fmt  = '%Y:%m:%d %H:%M:%S'
timestamp_file_fmt = '%Y-%m-%d_%H-%M-%S'


def setup(
        tool: str, 
        description: str, 
        epilog: str = '', 
        add_arguments: Callable[[argparse.ArgumentParser], None] = None,
        omit_arguments: {str} = {}
    ) -> (argparse.Namespace, logging.Logger):
    parser = parser_with_common_args(
        tool, 
        description,
        epilog=epilog,
        omit_arguments=omit_arguments)
    if add_arguments:
        add_arguments(parser)
    args = parser.parse_args()
    logger = make_logger(args.log_file, name=tool, level=args.log_level)
    log_args(logger, tool, args, epilog=epilog)
    return args, logger

def parser_with_common_args(tool: str, description: str, epilog: str = None, omit_arguments: {str} = {}) -> argparse.ArgumentParser:
    """
    Returns an `ArgumentParser` with the default arguments and a format string 
    that can be used by the calling program to print the actual values specified
    by the user.
    """
    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    if not 'model' in omit_arguments:
        parser.add_argument("-m", "--model", default=common_defaults['model'], 
            help=f"Use MODEL. Default {common_defaults['model']}")
    if not 'service-url' in omit_arguments:
        parser.add_argument("-s", "--service-url", default=common_defaults['service-url'],
            help=f"Use SERVICE_URL as the inference hosting service URL. Default: {common_defaults['service-url']}")
    if not 'template-dir' in omit_arguments:
        parser.add_argument("-t", "--template-dir", default=common_defaults['template-dir'],
            help=f"Use TEMPLATE_DIR as the location to find the prompt templates used. Default: {common_defaults['template-dir']}")
    if not 'data-dir' in omit_arguments:
        parser.add_argument("-d", "--data-dir", default=common_defaults['data-dir'], 
            help=f"Directory where data files are read or written. Default: {common_defaults['data-dir']}")
    if not 'use-cases' in omit_arguments:
        all_ucs = ', '.join([f"'{key}'" for key in all_use_cases().keys()])
        parser.add_argument("-u", "--use-cases", nargs="*",
            help=f"One or more uses cases to process. Quote them when the names have spaces. to specify more than one. Default: {all_ucs}")
    if not 'log-file' in omit_arguments:
        default_log_file = get_default_log_file(tool)
        default_log_level = get_default_log_level(tool)
        parser.add_argument("-l", "--log-file", default=default_log_file, 
            help=f"Where logging is written. Default: {default_log_file}.")
        parser.add_argument("--log-level", default=logging.INFO, type=int, 
            help=f"The integer value for the logging level (see https://docs.python.org/3/library/logging.html#logging-levels) is written. Default: {default_log_level} ({logging_level_to_string(default_log_level)}).")
    if not 'verbose' in omit_arguments:
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

def all_use_cases() -> dict:
    """
    Return a dictionary with the use case names as keys 
    and the corresponding expected labels as values.
    NOTE: This list must be kept consistent with the available prompt templates, etc.!
    """
    return {
        "prescription-refills": "refill",
        "non-prescription-refills": "other",
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
    print(f'** Logging to {log_file}, level {level_str} **')    
    return logger

def make_parent_dirs(file: str, exist_ok: bool = True) -> Path:
    path = Path(file)
    dot = Path('.')
    # If there is no parent prefix or possibly '.', return Path('.')
    if dot == path.parent:
        return dot
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

def parse_json(text: any) -> dict[str,any]:
    """Parse a JSON string, returning a dictionary or raise a ValueError error string if parsing fails."""
    try:
        obj = json.loads(text)
        return obj
    except (JSONDecodeError, TypeError) as err:
        raise ValueError(f"JSONDecodeError {err}: text not JSON? <{text}> (type: {type(text)})") from err


def extract_jsonl(text: str) -> [str]:
    """
    Sometimes the JSONL we ask for comes back without line feeds between the JSONL docs!
    Try to detect and fix this while splitting the string into JSONL lines. 
    If this attempt fails for some lines, just return those lines as is.
    """
    jsonl_re = re.compile(r'}\s*{')
    jsonls = []
    if not text.strip():
        return []
    for s in text.split('\n'):
        try:
            jsonl = parse_json(s)
            # It parsed! Use s
            jsonls.append(s)
        except ValueError as err:
            strs = jsonl_re.split(s)
            len_strs = len(strs)
            for i in range(len_strs):
                s2 = strs[i]
                # Hacks: add the '}' and '{' back. The first and last array elements are special cases.
                s2a = s2  if i == 0 else '{'+s2
                s2b = s2a if i == len_strs-1 else s2a+'}'
                try:
                    jsonl2 = parse_json(s2b)
                    # It parsed! Use s2b
                    jsonls.append(s2b)
                except ValueError as err2:
                    # just use s2 as is
                    jsonls.append(s2)
    return jsonls

# TODO: This is duplicated now in the HandleResponse class, which is used by
# the ChatBot app, but not by the "tools".
def extract_content(litellm_reponse: ModelResponse) -> str:
    """Returns the JSON-formatted string content we care about."""
    response_dict = litellm_reponse.to_dict()
    # TODO: There must be an easier way to get the "content"!!!
    content = response_dict['choices'][0]['message']['content']
    # print(f"content (type = {type(content)}: {content})")
    return content

def dict_pop(d: dict[str,any], key: str) -> any:
    """
    Works like dict.pop() should work; rather than raise an exception, 
    just return None and don't modify the dictionary.
    """
    try:
        return d.pop(key)
    except KeyError:
        return None
