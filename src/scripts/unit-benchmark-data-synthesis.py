import os
import sys
import argparse
import json
from pathlib import Path

from litellm import completion
from openai import OpenAIError
from utils import info, warning, error, load_yaml, model_dir_name, use_cases, ensure_dir_exists, extract_content

# Default settings
default_model = "ollama/gpt-oss:20b"
default_service_url = "http://localhost:11434"
default_template_dir = "src/prompts/templates"
default_data_dir = "data"

default_model_dir_name = model_dir_name(default_model)

def template_name(which_one: str) -> str:
    """Return a synthetic q and a patient chatbot template name."""
    return f"synthetic-q-and-a_patient-chatbot-{which_one}"

def check_label(json_line: str, expected_label: str, output_file) -> bool:
    try:
        js = json.loads(json_line)
        label = js['answer']['label']
        return expected_label == label
    except KeyError as ke:
        warning(f" JSON doesn't have a label field (exception: {ke}): {line}", files=[output_file])
    except json.decoder.JSONDecodeError as je:
        warning(f" JSON parsing failed (exception: {je}): {line}", files=[output_file])
    return False

def expected_lines(expected_label: str, data_file: str, output_file) -> int:
    """Check if all lines in the data file have the expected label."""
    try:
        with open(data_file, 'r') as f:
            unexpected_lines=[]
            for line in f.readlines():
                line2 = line.strip()
                if len(line2) == 0:
                    continue  # skip blanks
                if not check_label(line2, expected_label, output_file):
                    unexpected_lines.append(line2)
            if len(unexpected_lines) > 0:
                warning(f"{len(unexpected_lines)} lines in {data_file} do not have expected label {expected_label}!", files=[output_file])
                warning("The labels may be correct for the actual question generated, so please check them. Here they are:", files=[output_file])
                for line in unexpected_lines:
                    warning(f"  {line}", files=[output_file])
                return len(unexpected_lines)
            return 0
    except FileNotFoundError:
        error(f"Data file {data_file} not found.", files=[output_file])
        return -1  # doesn't get here; error exits, but we have this here for typing...

def do_generate(model_name: str, service_url: str, output_file, data_file: str, template: dict, expected_label: str) -> int:
    try:
        content = template['prompt']
        if len(content) == 0:
            error(f"The template['prompt'] is empty: template:\n{template}")
        response = completion(
            model = model_name, 
            messages = [{ 
                # "content": f"PROMPT:\n {template['prompt']}",
                "content": content,
                "role": "user",
            }], 
            api_base = service_url, 
            stream = False,
            # format = "json",
        )
        actual = extract_content(response)
        with open(data_file, 'w') as f:
            f.write(actual)
        with open(data_file, 'r') as f:
            num_qa_pairs=sum(1 for line in f.readlines() if 'question:' in line)
            info(f"Approximately {num_qa_pairs} Q&A pairs generated.", files=[output_file])
        
        # Check if all lines have the expected label
        num_unexpected_lines = expected_lines(expected_label, data_file, output_file)
        return num_unexpected_lines

    except OpenAIError as e:
        error(f"OpenAIError thrown: {e}", files=[output_file]) # error exits

def generate(model_name: str, service_url: str, template_dir: str, output_file, data_dir: str, which_one: str, expected_label: str):
    """Generate data with the given template and expected label."""
    ensure_dir_exists(template_dir, "template", files=[output_file])
    ensure_dir_exists(data_dir,     "data",     files=[output_file])
    template_n  = template_name(which_one)
    template = load_yaml(Path(template_dir, template_n+".yaml"))
    data_file = os.path.join(data_dir, f"{template_n}-data.json")
    
    info(f"  For expected label: {expected_label}:", files=[output_file])
    info(f"    Template:    {template_n}", files=[output_file])
    info(f"    Data file:   {data_file}", files=[output_file])
    
    num_unexpected_lines = do_generate(model_name, service_url, output_file, data_file, template, expected_label)
    if num_unexpected_lines > 0:
        warning(f"Run for {template_n} had {num_unexpected_lines} with the wrong labels or other errors. See data file {data_file}", files=[output_file])
    return num_unexpected_lines

def main():
    parser = argparse.ArgumentParser(description="Generate Q&A pairs for the healthcare ChatBot.")
    parser.add_argument("-m", "--model", default=default_model, help="Use MODEL instead of the default")
    parser.add_argument("-s", "--service-url", help=f"Use SERVICE_URL as the inference hosting service URL. Default: {default_service_url}")
    parser.add_argument("-t", "--template-dir", help=f"Use TEMPLATE_DIR as the location to find the prompt templates used. Default: {default_template_dir}")
    parser.add_argument("-o", "--output", default=None, help="Where standard output is written. Defaults to stdout.")
    parser.add_argument("-d", "--data", default=default_data_dir, help="Directory where data files are written. Default: {}".format(default_data_dir))
    
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
    info(f"{sys.argv[0]}:", files=[output_file])
    info(f"  Model:        {model_name}", files=[output_file])
    info(f"  Service URL:  {service_url}", files=[output_file])
    info(f"  Template dir: {template_dir}", files=[output_file])
    info(f"  Output:       {output_file_msg}", files=[output_file])
    info(f"  Data dir:     {data_dir}", files=[output_file])
    
    # Create the data directory
    os.makedirs(data_dir, exist_ok=True)

    for name, label in use_cases().items():
        substr = name.replace(' ', '-')
        generate(model_name, service_url, template_dir, output_file, data_dir, substr, label)

if __name__ == "__main__":
    main()
