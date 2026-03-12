import glob
import io
from litellm.types.utils import ModelResponse
from litellm.litellm_core_utils.streaming_handler import CustomStreamWrapper
import os
import re
import sys
import json
import logging
from pathlib import Path

from litellm import completion
from openai import OpenAIError
from common.utils import (
    all_use_cases,
    ensure_dirs_exist, 
    extract_content, 
    extract_jsonl
    load_yaml, 
    make_full_prompt, 
)

class UnitBenchmarkDataParent:

    template_prefix = 'synthetic-q-and-a_patient-chatbot'

    def __init__(self, 
        model_name: str, 
        service_url: str, 
        template_dir: str, 
        data_dir: str, 
        use_cases: [str], 
        logger: logging.Logger):
        self.model_name      = model_name
        self.service_url     = service_url
        self.template_dir    = template_dir
        self.data_dir        = data_dir
        self.logger          = logger

        all_ucs = all_use_cases()
        self.use_cases = {}
        if not use_cases:
            self.use_cases = all_ucs
        else:
            errors = []
            for uc in use_cases:
                if not uc in all_ucs:
                    errors.append(uc)
                else:
                    self.use_cases[uc] = all_ucs[uc]
            if errors:
                raise ValueError(f"One or more specified use cases [{', '.join(errors)}] not in known list: {list(all_ucs.keys())}")

        ensure_dirs_exist(self.template_dir)

class UnitBenchmarkDataSynthesizer(UnitBenchmarkDataParent):

    def __init__(self, 
        model_name: str, 
        service_url: str, 
        template_dir: str, 
        data_dir: str, 
        use_cases: [str], 
        logger: logging.Logger):
        super().__init__(
            model_name,
            service_url,
            template_dir,
            data_dir,
            use_cases,
            logger)

        # Create the data directory
        os.makedirs(self.data_dir, exist_ok=True)

    def template_name(self, which_one: str) -> str:
        return f"{self.template_prefix}-{which_one}"

    def check_label(self, json_line: str, expected_label: str) -> bool:
        try:
            js = json.loads(json_line)
            label = js['answer']['label']
            return expected_label == label
        except KeyError as ke:
            self.logger.warning(f" JSON doesn't have a label field (exception: {ke}): {json_line}")
        except json.decoder.JSONDecodeError as je:
            self.logger.warning(f" JSON parsing failed (exception: {je}): {json_line}")
        except Exception as e:
            self.logger.warning(f" JSON malformed? (Other exception thrown: {e}): {json_line}")
        return False

    def expected_lines(self, expected_label: str, data_file: str) -> int:
        """Check if all lines in the data file have the expected label."""
        try:
            with open(data_file, 'r') as f:
                unexpected_lines=[]
                for line in f.readlines():
                    line2 = line.strip()
                    if len(line2) == 0:
                        continue  # skip blanks
                    if not self.check_label(line2, expected_label):
                        unexpected_lines.append(line2)
                if len(unexpected_lines) > 0:
                    self.logger.warning(f"{len(unexpected_lines)} lines in {data_file} do not have expected label {expected_label}!")
                    self.logger.warning("The labels may be correct for the actual question generated, so please check them. Here they are:")
                    for line in unexpected_lines:
                        self.logger.warning(f"  {line}")
                    return len(unexpected_lines)
                return 0
        except FileNotFoundError:
            self.logger.error(f"Data file {data_file} not found.")
            sys.exit(1)

    def do_generate(self, data_file: str, template: dict, expected_label: str) -> int:
        try:
            content = template['prompt']
            if len(content) == 0:
                self.logger.error(f"The template['prompt'] is empty: template:\n{template}")
                sys.exit(1)
            response = completion(
                model = self.model_name, 
                messages = [{ 
                    # "content": f"PROMPT:\n {template['prompt']}",
                    "content": content,
                    "role": "user",
                }], 
                api_base = self.service_url, 
                stream = False,
                verbose = False,
                # format = "json",
            )
            jsonls = extract_jsonl(extract_content(response))
            with open(data_file, 'w') as f:
                for line in jsonls:
                    f.write(line)
            with open(data_file, 'r') as f:
                num_qa_pairs=sum(1 for line in f.readlines() if '"question":' in line)
                self.logger.info(f"Approximately {num_qa_pairs} Q&A pairs generated.")
            
            # Check if all lines have the expected label
            num_unexpected_lines = self.expected_lines(expected_label, data_file)
            return num_unexpected_lines

        except OpenAIError as e:
            self.logger.error(f"OpenAIError thrown: {e}")
            sys.exit(1)

    def generate_data_for_use_case(self, which_one: str, expected_label: str) -> int:
        """Generate data for the given use case with its expected label."""
        template_n  = self.template_name(which_one)
        template = load_yaml(Path(self.template_dir, template_n+".yaml"))
        data_file = os.path.join(self.data_dir, f"{template_n}-data.jsonl")
        
        self.logger.info(f"  For expected label: {expected_label}:")
        self.logger.info(f"    Template:    {template_n}")
        self.logger.info(f"    Data file:   {data_file}")
        
        num_unexpected_lines = self.do_generate(data_file, template, expected_label)
        if num_unexpected_lines > 0:
            self.logger.warning(f"Run for {template_n} had {num_unexpected_lines} with the wrong labels or other errors. See data file {data_file}")
        return num_unexpected_lines

    def generate_data(self) -> int:
        """Generate data for all use cases with the expected labels."""
        count = 0
        for name, label in self.use_cases.items():
            count += self.generate_data_for_use_case(name, label)
        return count

class UnitBenchmarkDataValidator(UnitBenchmarkDataParent):

    template_prefix = "synthetic-q-and-a_patient-chatbot-data-validation"

    def __init__(self, model_name: str, 
        service_url: str, 
        template_dir: str, 
        data_dir: str, 
        use_cases: [str], 
        just_stats: bool, 
        logger: logging.Logger):
        super().__init__(
            model_name,
            service_url,
            template_dir,
            data_dir,
            use_cases,
            logger)
        self.just_stats = just_stats
        ensure_dirs_exist(self.data_dir)

        template_file = Path(template_dir, self.template_prefix+".yaml")
        self.logger.info(f"Using template file: {template_file}")
        self.template = load_yaml(template_file)

    def get_rating(self, line: str, line_number: int) -> int:
        try:
            js = json.loads(line)
            return js['rating']
        except KeyError as ke:
            self.logger.warning(f" JSON doesn't have a rating field (exception: {ke}):  line #{line_number} = {line}")
        except json.decoder.JSONDecodeError as je:
            self.logger.warning(f" JSON parsing failed (exception: {je}): line #{line_number} = {line}")
        return -1

    def return_stats(self, data_file: str, validation_file: str) -> dict:
        ratings = [0 for i in range(5)]
        total_count = 0
        error_count = 0
        with open(validation_file, 'r') as f:
            for line in f.readlines():
                if len(line.strip()) == 0:
                    continue
                total_count += 1
                rating = self.get_rating(line, total_count)
                if rating < 0:
                    error_count += 1
                elif rating > 5:
                    error_count += 1
                    self.logger.warning("Rating > 5: {line}")
                else:
                    r = ratings[rating-1]
                    ratings[rating-1] = r+1
        return {
            'data-file': data_file, 
            'validation-file': validation_file, 
            'ratings': ratings, 
            'total_count': total_count, 
            'error_count': error_count
        }

    def validate_line(self, line: str, system_prompt: str, validation_file: io.TextIOWrapper):
        """Validate a single generated datum; does the question match the label?"""    
        try:
            response: ModelResponse | CustomStreamWrapper = completion(
                model = self.model_name, 
                messages = [{ 
                    "content": make_full_prompt(line, system_prompt),
                    "role": "user",
                }], 
                api_base = self.service_url, 
                stream = False,
                verbose = False,
                # format = "json",
            )
            for line in extract_jsonl(extract_content(response)):
                validation_file.write(f"{line}\n")

        except OpenAIError as e:
            self.logger.error(f"OpenAIError thrown: {e}")
            sys.exit(1)

    def validate(self) -> dict:
        """Validate the generated data labeling."""    
        system_prompt = self.template['system']
        if len(system_prompt) == 0:
            self.logger.error(f"The template['system'] is empty: template:\n{self.template}")
            sys.exit(1)

        total_stats = {}

        globs = [f"*-{name}-data.jsonl" for name in self.use_cases]
        data_file_names = []
        for gl in globs:
            for files in glob.iglob(gl, root_dir=self.data_dir, recursive=False, include_hidden=False):
                data_file_names.append(files)
        self.logger.info(f"Validating data files: {data_file_names}")
        print(f"Validating data files: {data_file_names}")
        for data_file_name in data_file_names:
            data_file = os.path.join(self.data_dir, data_file_name)
            validation_file = os.path.splitext(data_file)[0]+'-validation.jsonl' 
            if not self.just_stats:
                with open(validation_file, 'w') as vfile:
                    with open(data_file, 'r') as synthetic_data_file:
                        synth_data = synthetic_data_file.readlines()
                        for line in extract_jsonl(synth_data):
                            line2 = line.strip()
                            if len(line2) == 0:
                                continue
                            self.validate_line(line2, system_prompt, vfile)

            stats = self.return_stats(data_file, validation_file)
            total_stats.update({data_file: stats})
        return total_stats

    def print_stats(self, stats: dict):
        name_len = 80 # hack
        name_fmt = '{:' + f"{name_len}" + 's}  |'
        col_fmt  = '  {:3d}  |'
        border_fmt = '{:'+f"{name_len}"+"s}  |-------|-------|-------|-------|-------|-------|"
        
        line = [name_fmt.format("Files:")]
        [line.append(col_fmt.format(i+1)) for i in range(5)]
        line.append(' Total |')
        self.logger.info("".join(line))

        self.logger.info(border_fmt.format("-"*name_len))

        all_ratings = [0 for i in range(5)]
        all_count = 0
        all_error_count = 0
        for data_file, stts in stats.items():
            syn_data_file   = stts['data-file']
            validation_file = stts['validation-file']
            ratings         = stts['ratings']
            total_count     = stts['total_count']
            error_count     = stts['error_count']
            dfile = os.path.split(syn_data_file)[1]
            line = [name_fmt.format(dfile)]
            [line.append(col_fmt.format(ratings[i])) for i in range(5)]
            line.append(col_fmt.format(sum(ratings)))
            self.logger.info("".join(line))

            for i in range(5):
                tri = all_ratings[i]
                all_ratings[i] = tri + ratings[i]
            all_count += total_count
            all_error_count += error_count

        self.logger.info(border_fmt.format("-"*name_len))
        line = [name_fmt.format("Totals:")]
        [line.append(col_fmt.format(all_ratings[i])) for i in range(5)]
        line.append(col_fmt.format(sum(all_ratings)))
        self.logger.info("".join(line))
        self.logger.info(border_fmt.format("-"*name_len))
        self.logger.info(f"Total count: {all_count} (includes errors), total errors: {all_error_count}")
