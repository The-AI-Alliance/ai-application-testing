import os
import sys
import argparse
import json
import glob
from pathlib import Path

from litellm import completion
from openai import OpenAIError
from utils import info, warning, error, load_yaml, model_dir_name, use_cases, ensure_dir_exists, make_full_prompt, extract_content

# Default settings
default_model = "ollama/gpt-oss:20b"
default_service_url = "http://localhost:11434"
default_template_dir = "src/prompts/templates"
default_data_dir = "data"
default_model_dir_name = model_dir_name(default_model)

def get_rating(line: str, output_file) -> int:
    try:
        js = json.loads(line)
        return js['rating']
    except KeyError as ke:
        warning(f" JSON doesn't have a rating field (exception: {ke}): {line}", files=[output_file])
    except json.decoder.JSONDecodeError as je:
        warning(f" JSON parsing failed (exception: {je}): {line}", files=[output_file])
    return -1

def return_stats(data_file: str, validation_file: str, output_file) -> dict:
    ratings = [0 for i in range(5)]
    total_count = 0
    error_count = 0
    with open(validation_file, 'r') as f:
        for line in f.readlines():
            if len(line.strip()) == 0:
                continue
            total_count += 1
            rating = get_rating(line, output_file)
            if rating < 0:
                error_count += 1
            elif rating > 5:
                error_count += 1
                warning("Rating > 5: {line}", files=[output_file])
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

def validate_line(line: str, model_name: str, service_url: str, system_prompt: str, output_file, validation_file):
    """Validate a single generated datum; does the question match the label?"""    
    try:
        response = completion(
            model = model_name, 
            messages = [{ 
                "content": make_full_prompt(line, system_prompt),
                "role": "user",
            }], 
            api_base = service_url, 
            stream = False,
            # format = "json",
        )
        actual = extract_content(response)
        validation_file.write(actual+"\n")

    except OpenAIError as e:
        error(f"OpenAIError thrown: {e}", files=[output_file]) # error exits

def validate(just_stats: bool, model_name: str, service_url: str, template: dict, output_file, data_dir: str) -> dict:
    """Validate the generated data labeling."""    
    system_prompt = template['system']
    if len(system_prompt) == 0:
        error(f"The template['system'] is empty: template:\n{template}")

    total_stats = {}
    for data_file_name in glob.iglob('*-data.json', root_dir=data_dir, recursive=False, include_hidden=False):
        data_file = os.path.join(data_dir, data_file_name)
        validation_file = os.path.splitext(data_file)[0]+'-validation.json' 
        if not just_stats:
            with open(validation_file, 'w') as vfile:
                with open(data_file, 'r') as synthetic_data_file:
                    for line in synthetic_data_file.readlines():
                        line2 = line.strip()
                        if len(line2) == 0:
                            continue
                        validate_line(line2, model_name, service_url, system_prompt, output_file, vfile)

        stats = return_stats(data_file, validation_file, output_file)
        total_stats.update({data_file: stats})
    return total_stats

def print_stats(stats: dict, output_file):
    name_len = 80 # hack
    name_fmt = '{:' + f"{name_len}" + 's}  |'
    col_fmt  = '  {:3d}  |'
    border_fmt = '{:'+f"{name_len}"+"s}  |-------|-------|-------|-------|-------|-------|"
    
    line = [name_fmt.format("Files:")]
    [line.append(col_fmt.format(i+1)) for i in range(5)]
    line.append(' Total |')
    info("".join(line), files=[output_file])

    info(border_fmt.format("-"*name_len), files=[output_file])

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
        info("".join(line), files=[output_file])

        for i in range(5):
            tri = all_ratings[i]
            all_ratings[i] = tri + ratings[i]
        all_count += total_count
        all_error_count += error_count

    info(border_fmt.format("-"*name_len), files=[output_file])
    line = [name_fmt.format("Totals:")]
    [line.append(col_fmt.format(all_ratings[i])) for i in range(5)]
    line.append(col_fmt.format(sum(all_ratings)))
    info("".join(line), files=[output_file])
    info(border_fmt.format("-"*name_len), files=[output_file])
    info(f"Total count: {all_count} (includes errors), total errors: {all_error_count}", files=[output_file])

def main():
    parser = argparse.ArgumentParser(description="Generate Q&A pairs for the healthcare ChatBot.")
    parser.add_argument("-m", "--model", default=default_model, 
        help=f"Use MODEL. Default {default_model}")
    parser.add_argument("-s", "--service-url", default=default_service_url,
        help=f"Use SERVICE_URL as the inference hosting service URL. Default: {default_service_url}")
    parser.add_argument("-t", "--template-dir", default=default_template_dir,
        help=f"Use TEMPLATE_DIR as the location to find the prompt templates used. Default: {default_template_dir}")
    parser.add_argument("-o", "--output", default=None, 
        help="Where standard output is written. Defaults to stdout.")
    parser.add_argument("-d", "--data", default=default_data_dir, 
        help=f"Directory where data files are written. Default: {default_data_dir}")
    parser.add_argument("-j", "--just-stats", action='store_true', default=False, 
        help="Just report the final statistics for existing validation data. Default: False")
    
    args = parser.parse_args()
    
    model_name = args.model
    service_url = args.service_url if args.service_url else default_service_url
    template_dir = args.template_dir if args.template_dir else default_template_dir
    data_dir = args.data
    output_file = sys.stdout
    output_file_msg = 'stdout'
    if args.output:
        output_file = open(args.output, "w") 
        output_file_msg = args.output 

    ensure_dir_exists(template_dir, "template", files=[output_file])
    ensure_dir_exists(data_dir,     "data",     files=[output_file])
    template_n = "synthetic-q-and-a_patient-chatbot-data-validation"
    template_file = Path(template_dir, template_n+".yaml")
    template = load_yaml(template_file)

    info(f"{sys.argv[0]}:", files=[output_file])
    info(f"  Model:             {model_name}", files=[output_file])
    info(f"  Service URL:       {service_url}", files=[output_file])
    info(f"  Template:          {template_file}", files=[output_file])
    info(f"  Output:            {output_file_msg}", files=[output_file])
    info(f"  Data dir:          {data_dir}", files=[output_file])
    info(f"  Just report stats? {args.just_stats}", files=[output_file])

    total_stats = validate(args.just_stats, model_name, service_url, template, output_file, data_dir)
    print_stats(total_stats, output_file)

if __name__ == "__main__":
    main()
