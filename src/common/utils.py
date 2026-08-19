"""Miscellaneous utilities."""

# Allow types to self-reference during their definitions.
from __future__ import annotations

import argparse
import logging
import os
from collections.abc import Callable, Mapping, Sequence
from importlib import metadata
from pathlib import Path
from typing import Any

from litellm.types.utils import ModelResponse

from common.date_time_utils import now, now_str, timestamp_file_fmt

from .collections import get_chain

# Too many of these warnings for variables that ARE used in other files.
# pylint: disable=unused-variable

common_defaults = {
    "model": "ollama_chat/gemma4:12b",
    "service-url": "http://localhost:11434",
    "template-dir": "prompts/templates",
    "data-dir": "data",
    "output-dir": "output",
    "levenshtein-ratio-threshold": 0.95,
}


class ExpectedFail:  # pylint: disable=too-few-public-methods
    """Utility to handle a callable that is expected to raise an exception of a particular type."""

    def __init__(self, expected_type: type[BaseException]):
        self.expected_type = expected_type
        self.expected_name = self.expected_type.__name__

    def __call__(self, block: Callable[[], Any], verbose: bool = False):
        try:
            block()
        except self.expected_type as err:
            if verbose:
                print(f"Okay: expected exception type {self.expected_name} received: {err}.")
            return
        except BaseException as err:  # noqa: BLE001 pylint: disable=broad-exception-caught
            assert False, f'Exception of type {type(err).__name__} ("{err}") received. Expected {self.expected_name}.'

        assert False, f"No exception occurred. Expected exception of type {self.expected_name}."


def tool_setup(
    tool: str,
    description: str,
    epilog: str = "",
    add_arguments: Callable[[argparse.ArgumentParser], Any | None] = lambda ap: None,
    omit_arguments: set[str] | None = None,
) -> tuple[argparse.Namespace, logging.Logger]:
    """Common setup steps for command line tools."""
    parser = parser_with_common_args(tool, description, epilog=epilog, omit_arguments=omit_arguments)
    add_arguments(parser)
    args = parser.parse_args()
    logger = make_logger(args.log_file, name=tool, level=args.log_level)
    _log_args(logger, tool, args, epilog=epilog)
    return args, logger


def parser_with_common_args(
    tool: str, description: str, epilog: str = "", omit_arguments: set[str] | None = None
) -> argparse.ArgumentParser:
    """
    Returns an `ArgumentParser` with the default arguments and a format string
    that can be used by the calling program to print the actual values specified
    by the user.
    """
    omit_args: set[str] = omit_arguments if omit_arguments else set()

    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    if "model" not in omit_args:
        parser.add_argument(
            "-m",
            "--model",
            default=common_defaults["model"],
            help=f"Use MODEL. Default {common_defaults['model']}",
        )
    if "service-url" not in omit_args:
        parser.add_argument(
            "-s",
            "--service-url",
            default=common_defaults["service-url"],
            help=f"Use SERVICE_URL as the inference hosting service URL. Default: {common_defaults['service-url']}",
        )
    if "template-dir" not in omit_args:
        parser.add_argument(
            "-t",
            "--template-dir",
            default=common_defaults["template-dir"],
            help=f"Use TEMPLATE_DIR as the location to find the prompt templates used. Default: {common_defaults['template-dir']}",
        )
    if "data-dir" not in omit_args:
        parser.add_argument(
            "-d",
            "--data-dir",
            default=common_defaults["data-dir"],
            help=f"Directory where data files are read or written. Default: {common_defaults['data-dir']}",
        )
    if "output-dir" not in omit_args:
        parser.add_argument(
            "-o",
            "--output-dir",
            default=common_defaults["output-dir"],
            help=f"Directory where some output files are read or written (may not be used). Default: {common_defaults['output-dir']}",
        )
    if "use-cases" not in omit_args:
        all_ucs = ", ".join([f"'{key}'" for key in all_use_cases()])
        parser.add_argument(
            "-u",
            "--use-cases",
            nargs="*",
            help=f"One or more uses cases to process. Quote them when the names have spaces. to specify more than one. Default: {all_ucs}",
        )
    if "log-file" not in omit_args:
        default_log_file = _get_default_log_file(tool)
        default_log_level = logging.INFO
        parser.add_argument(
            "-l",
            "--log-file",
            default=default_log_file,
            help=f"Where logging is written. Default: {default_log_file}.",
        )
        parser.add_argument(
            "--log-level",
            default=logging.INFO,
            type=int,
            help=f"The integer value for the logging level (see https://docs.python.org/3/library/logging.html#logging-levels) is written. Default: {default_log_level} ('logging.INFO').",
        )
    if "verbose" not in omit_args:
        parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="Print some extra output. Useful for some testing and debugging scenarios.",
        )
    return parser


def _add_info_str(label: str, value: str, separator: str = ":") -> str:
    lbl = label + separator
    return f"  {lbl:20s} {value}"


def _logging_level_to_string(logger: logging.Logger, level: int = -1):
    if level < 0:
        level = logger.getEffectiveLevel()
    return logging.getLevelName(level)


def _log_args(logger: logging.Logger, tool: str, args: argparse.Namespace, epilog: str = ""):
    logger.info(f" ({now()}) Running {tool} with these argument values:")
    for k, v in vars(args).items():
        if k == "log_level":
            v = f"{v} (== logger.{_logging_level_to_string(logger, v)})"
        logger.info(_add_info_str(k, v))

    if epilog:
        logger.info("")
        logger.info(" " + epilog)


def get_package_version(logger: logging.Logger) -> str | None:
    """
    Return the version string in the project's pyproject.toml. Note that we have to keep
    the name used below in sync with the name in that file: `ai-application-testing`.
    If the version information can't be determined, None is returned. This usually means that
    the project was not pip installed, i.e., `uv pip install -e .` We log this possibility.
    """
    try:
        version = metadata.version("ai-application-testing")
        if not version:
            logger.error(
                "The version string returned is empty. Make sure it is defined in pyproject.toml, then run 'uv pip install -e .'"
            )
            version = None
    except metadata.PackageNotFoundError as pnfe:
        logger.error(f"Could not determine the package version {pnfe}. Try running 'uv pip install -e .'")
        version = None
    return version


def model_dir_name(model: str) -> str:
    """Replace colon with underscore in the model name."""
    return model.replace(":", "_")


def all_use_cases() -> Mapping[str, Any]:
    """
    Return a Mapping with the use case names as keys
    and the corresponding expected labels as values.
    NOTE: This list must be kept consistent with the available prompt templates, etc.!
    """
    return {
        "prescription-refills": "refill",
        "non-prescription-refills": "other",
        "emergency": "emergency",
    }


def _get_default_log_file(tool_name: str) -> str:
    log_dir = f"logs/{now_str(fmt = timestamp_file_fmt)}"
    return f"{log_dir}/{tool_name}.log"


def make_logger(log_file: str, name: str = "__name__", level: int = logging.INFO) -> logging.Logger:
    """Convenience function to make a Logger instance."""
    make_parent_dirs(log_file)
    logging.basicConfig(filename=log_file, level=level)
    logger = logging.getLogger(name)
    logger.setLevel(level)

    level_str = logging.getLevelName(level)
    print(f"** Logging to {log_file}, level {level_str} **")
    return logger


def make_parent_dirs(file: str, exist_ok: bool = True) -> Path:
    """
    Create the parent directories for the input file path.
    This is a wrapper around `os.mkdirs()`, so the value for
    `exist_ok` is passed to it. If there is no parent directory path,
    then nothing is done and `Path(".")` is returned.
    """
    path = Path(file)
    dot = Path(".")
    if dot == path.parent:
        return dot
    dirs = path.parent
    os.makedirs(dirs, exist_ok=exist_ok)
    return dirs


def ensure_dirs_exist(*dirs) -> bool:
    """Raise a `ValueError` if any of the directories passed in don't exist."""
    missing_dirs = []
    for d in dirs:
        if not os.path.isdir(d):
            missing_dirs.append(d)
    if len(missing_dirs) > 0:
        raise ValueError(f"These directories don't exit: {', '.join(missing_dirs)}")
    return True  # most callers will ignore this...


def make_full_prompt(prompt: str, system_prompt: Any, session: Sequence[tuple[str, str]] | None = None) -> str:
    """Make a full prompt string from the input details."""
    ss = ["SESSION:"]
    if session:
        for query, reply in session:
            ss.append(f"query: {query}")
            ss.append(f"reply: {reply}")
            ss.append("\n")

    return f"""
SYSTEM PROMPT: 
{system_prompt}

USER PROMPT: 
{prompt}

{'\n'.join(ss)}
"""


def extract_content_from_model_response(litellm_response: ModelResponse) -> str:
    """Returns the JSON-formatted string content we care about."""
    response_dict = litellm_response.to_dict()
    # There really must be an easier way to get the "content"!!!
    content = get_chain(response_dict, ["choices", 0, "message", "content"])
    # print(f"content (type = {type(content)}: {content})")
    return content if content is not None else ""
