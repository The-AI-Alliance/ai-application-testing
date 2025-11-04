import os
import sys
import io
import json
import glob
import logging
from pathlib import Path

from litellm import completion
from openai import OpenAIError
from utils import (
    common_defaults, parse_common_args, 
    get_default_log_file, make_logger, 
    load_yaml, model_dir_name, ensure_dirs_exist, 
    use_cases, make_full_prompt, extract_content
)

class BenchMarkDataValidator:

    template_prefix = "synthetic-q-and-a_patient-chatbot-data-validation"

    def __init__(self, just_stats: bool, model_name: str, service_url: str, template_dir: str, data_dir: str, logger: logging.Logger):
        self.just_stats   = just_stats
        self.model_name   = model_name
        self.service_url  = service_url
        self.template_dir = template_dir
        self.data_dir     = data_dir
        self.logger       = logger

        template_file = Path(template_dir, self.template_prefix+".yaml")
        self.logger.info(f"Using template file: {template_file}")
        self.template = load_yaml(template_file)

    def get_rating(self, line: str) -> int:
        try:
            js = json.loads(line)
            return js['rating']
        except KeyError as ke:
            self.logger.warning(f" JSON doesn't have a rating field (exception: {ke}): {line}")
        except json.decoder.JSONDecodeError as je:
            self.logger.warning(f" JSON parsing failed (exception: {je}): {line}")
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
                rating = self.get_rating(line, )
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
            response = completion(
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
            actual = extract_content(response)
            validation_file.write(actual+"\n")

        except OpenAIError as e:
            self.logger.error(f"OpenAIError thrown: {e}")
            sys.exit(1)

    def validate(self) -> dict:
        """Validate the generated data labeling."""    
        system_prompt = self.template['system']
        if len(system_prompt) == 0:
            self.logger.error(f"The template['system'] is empty: template:\n{template}")
            sys.exit(1)

        total_stats = {}
        for data_file_name in glob.iglob('*-data.json', root_dir=self.data_dir, recursive=False, include_hidden=False):
            data_file = os.path.join(self.data_dir, data_file_name)
            validation_file = os.path.splitext(data_file)[0]+'-validation.json' 
            if not self.just_stats:
                with open(validation_file, 'w') as vfile:
                    with open(data_file, 'r') as synthetic_data_file:
                        for line in synthetic_data_file.readlines():
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

def main():

    script = os.path.basename(__file__)
    parser = parse_common_args("Validate synthesized Q&A pairs for the healthcare ChatBot.", script)
    parser.add_argument("-j", "--just-stats", action='store_true', default=False, 
        help="Just report the final statistics for existing validation data. Default: False")    
    args = parser.parse_args()
    
    logger = make_logger(args.log)
    print(f'Logging to {args.log}, level INFO')

    ensure_dirs_exist([args.template_dir, args.data_dir], logger)

    logging.info(f"{script}:")
    logging.info(f"  Model:             {args.model}")
    logging.info(f"  Service URL:       {args.service_url}")
    logging.info(f"  Template dir:      {args.template_dir}")
    logging.info(f"  Data dir:          {args.data_dir}")
    logging.info(f"  Just report stats? {args.just_stats}")
    logging.info(f"  Log:               {args.log}")

    validator = BenchMarkDataValidator(
        args.just_stats, args.model, args.service_url, args.template_dir, args.data_dir, logger)
     
    total_stats = validator.validate()
    validator.print_stats(total_stats)

if __name__ == "__main__":
    main()
