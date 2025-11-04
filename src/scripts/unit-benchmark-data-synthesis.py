import os
import sys
import json
import logging
from pathlib import Path

from litellm import completion
from openai import OpenAIError
from utils import (
    common_defaults, parse_common_args, get_default_log_file, make_logger, 
    load_yaml, model_dir_name, ensure_dirs_exist, 
    use_cases, extract_content
)

class BenchMarkDataSynthesizer:

    template_prefix = 'synthetic-q-and-a_patient-chatbot'

    def __init__(self, model_name: str, service_url: str, template_dir: str, data_dir: str, logger: logging.Logger):
        self.model_name      = model_name
        self.service_url     = service_url
        self.template_dir    = template_dir
        self.data_dir        = data_dir
        self.logger          = logger
        # Create the data directory
        os.makedirs(self.data_dir, exist_ok=True)
        ensure_dirs_exist([self.template_dir, self.data_dir], self.logger)

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
            actual = extract_content(response)
            with open(data_file, 'w') as f:
                f.write(actual)
            with open(data_file, 'r') as f:
                num_qa_pairs=sum(1 for line in f.readlines() if 'question:' in line)
                self.logger.info(f"Approximately {num_qa_pairs} Q&A pairs generated.")
            
            # Check if all lines have the expected label
            num_unexpected_lines = self.expected_lines(expected_label, data_file)
            return num_unexpected_lines

        except OpenAIError as e:
            self.logger.error(f"OpenAIError thrown: {e}")
            sys.exit(1)

    def generate(self, which_one: str, expected_label: str) -> int:
        """Generate data with the given template and expected label."""
        template_n  = self.template_name(which_one)
        template = load_yaml(Path(self.template_dir, template_n+".yaml"))
        data_file = os.path.join(self.data_dir, f"{template_n}-data.json")
        
        self.logger.info(f"  For expected label: {expected_label}:")
        self.logger.info(f"    Template:    {template_n}")
        self.logger.info(f"    Data file:   {data_file}")
        
        num_unexpected_lines = self.do_generate(data_file, template, expected_label)
        if num_unexpected_lines > 0:
            self.logger.warning(f"Run for {template_n} had {num_unexpected_lines} with the wrong labels or other errors. See data file {data_file}")
        return num_unexpected_lines

    def generate_all(self):
        for name, label in use_cases().items():
            substr = name.replace(' ', '-')
            self.generate(substr, label)

def main():

    script = os.path.basename(__file__)
    parser = parse_common_args("Synthesize Q&A pairs for the healthcare ChatBot.", script)
    args = parser.parse_args()
    
    logger = make_logger(args.log)
    print(f'Logging to {args.log}, level INFO')

    logger.info(f"{script}:")
    logger.info(f"  Model:           {args.model}")
    logger.info(f"  Service URL:     {args.service_url}")
    logger.info(f"  Template dir:    {args.template_dir}")
    logger.info(f"  Data dir:        {args.data_dir}")
    logger.info(f"  Log:             {args.log}")
    
    synthesizer = BenchMarkDataSynthesizer(
        args.model, args.service_url, args.template_dir, args.data_dir, logger)
    synthesizer.generate_all()

if __name__ == "__main__":
    main()
