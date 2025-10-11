import sys
from pathlib import Path
from litellm import completion
from openai import OpenAIError
from utils import info, warning, error, load_yaml, make_full_prompt, extract_content

default_model = "ollama/gpt-oss:20b"
default_service_url = "http://localhost:11434"
default_template_dir = "src/prompts/templates"
default_data_dir = "data"

refill_queries = [
    "I need my _P_ refilled.",
    "I need my _P_ drug refilled.",
    "I'm out of _P_. Can I get a refill?",
    "I need more _P_.",
    "My pharmacy says I don't have any refills for _P_. Can you ask them to refill it?"
]
refill_expected_response = "Okay, I have your request for a refill for _P_. I will check your records and get back to you within the next business day."

other_queries = [
    "My prescription for _P_ upsets my stomach.",
    "I have trouble sleeping, ever since I started taking _P_.",
    "When is my next appointment?"
]
other_query_expected_response = "I have received your message, but I can't answer it right now. I will get back to you within the next business day."

template_names = [
    "q-and-a_patient-chatbot-prescriptions-with-examples",
    "q-and-a_patient-chatbot-prescriptions"
]

drugs = [
    "prozac",
    "xanax"
]

def trial(model_name, output_file, service_url, template_dir, label, expected_response, queries, template_names, drugs):
    """Performs trials for the given label and queries."""
    count = 0
    errors = 0
    info(f"Queries that are {label} requests:", files=[output_file])

    for template_name in template_names:
        info(f"  Using template {template_name} in {template_dir}:", files=[output_file])
        template = load_yaml(Path(template_dir, template_name+".yaml"))

        for query in queries:
            for drug in drugs:
                expected = expected_response.replace("_P_", drug)
                expected_lc = expected.lower()
                resp_str = "SUCCESS!"
                query_with_drug = query.replace("_P_", drug)

                try:
                    response = completion(
                        model = model_name, 
                        messages = [{ 
                            "content": make_full_prompt(query_with_drug, template['system']),
                            "role": "user",
                        }], 
                        api_base = service_url, 
                        stream = False,
                    )
                    count += 1
                    actual = extract_content(response)
                    if actual != expected:
                        actual_lc = actual.lower().strip()
                        # Remove leading `-` if present. Remove "*" around words.
                        actual_lc = actual_lc.lstrip("-").replace('*', '')
                        if actual_lc == expected_lc:
                            resp_str = f"{resp_str} (ignoring case differences and possible '*' Markdown-style formatting.)"
                        else:
                            resp_str = f"FAILURE! actual = {actual}, expected = {expected} (full response: {response})"
                            errors += 1

                    info(f"    Query: {query_with_drug} => {resp_str}", files=[output_file])

                except OpenAIError as e:
                    error(f"OpenAIError thrown: {e}", files=[output_file])

        info(f"Total queries = {count}, errors = {errors}", files=[output_file])

    if errors > 0:
        warning(f'"{label}" run had errors, but we will continue running.', files=[output_file])

def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model", help=f"Use MODEL as the inference model. Default: {default_model}")
    parser.add_argument("-s", "--service-url", help=f"Use SERVICE_URL as the inference hosting service URL. Default: {default_service_url}")
    parser.add_argument("-t", "--template-dir", help=f"Use TEMPLATE_DIR as the location to find the prompt templates used. Default: {default_template_dir}")
    parser.add_argument("-o", "--output", help="Where standard output is written. Defaults to stdout.")
    parser.add_argument("-d", "--data", default=default_data_dir, help="Directory where data files are written. IGNORED; NOT CURRENTLY USED! Default: {}".format(default_data_dir))
    args = parser.parse_args()

    model_name = args.model if args.model else default_model
    service_url = args.service_url if args.service_url else default_service_url
    template_dir = args.template_dir if args.template_dir else default_template_dir
    output_file = sys.stdout
    output_file_msg = 'stdout'
    if args.output:
        output_file = open(args.output, "w") 
        output_file_msg = args.output 
    data_dir = args.data

    info(f"{sys.argv[0]}:", files=[output_file])
    info(f"  Model:        {model_name}", files=[output_file])
    info(f"  Service URL:  {service_url}", files=[output_file])
    info(f"  Template dir: {template_dir}", files=[output_file])
    info(f"  Output:       {output_file_msg}", files=[output_file])
    # info(f"  Data dir:     {data_dir}", files=[output_file])

    trial(model_name, output_file, service_url, template_dir, "refill", refill_expected_response, refill_queries, template_names, drugs)
    trial(model_name, output_file, service_url, template_dir, "non-refill", other_query_expected_response, other_queries, template_names, drugs)

if __name__ == "__main__":
    main()
