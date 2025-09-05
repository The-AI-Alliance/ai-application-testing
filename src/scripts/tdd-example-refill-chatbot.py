import sys
from pathlib import Path
from litellm import completion
from openai import OpenAIError
from utils import error, load_yaml, replace_x

default_model = "ollama/gpt-oss:20b"
default_service_url = "http://localhost:11434"
default_template_dir = "src/llm/templates"

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

def make_content(prompt: str, system_prompt: dict) -> str:
    return f"""
SYSTEM PROMPT: 
{system_prompt}

PROMPT: 
{prompt}
"""

def trial(output_file, service_url, template_dir, label, expected_response, queries, template_names, drugs, model_name):
    """Performs trials for the given label and queries."""
    count = 0
    errors = 0
    output_file.write(f"Queries that are {label} requests:\n")

    for template_name in template_names:
        output_file.write(f"  Using template {template_name} in {template_dir}:\n")
        template = load_yaml(Path(template_dir, template_name+".yaml"))

        for query in queries:
            for drug in drugs:
                expected = replace_x("_P_", drug, expected_response)
                expected_lc = expected.lower()
                resp_str = "SUCCESS!"
                query_with_drug = replace_x("_P_", drug, query)

                try:
                    response = completion(
                        model = model_name, 
                        messages = [{ 
                            "content": make_content(query_with_drug, template['system']),
                            "role": "user",
                        }], 
                        api_base = service_url, 
                        stream = False,
                    )
                    count += 1
                    response_dict = response.to_dict()
                    # TODO: There must be an easier way to get the "content"!!!
                    actual = response_dict['choices'][0]['message']['content']
                    if actual != expected:
                        actual_lc = actual.lower().strip()
                        # Remove leading `-` if present. Remove "*" around words.
                        actual_lc = actual_lc.lstrip("-").replace('*', '')
                        if actual_lc == expected_lc:
                            resp_str = f"{resp_str} (ignoring case differences and possible '*' Markdown-style formatting.)"
                        else:
                            resp_str = f"FAILURE! actual = {actual}, expected = {expected} (full response: {response})"
                            errors += 1

                    output_file.write(f"    Query: {query_with_drug} => {resp_str}\n")

                except OpenAIError as e:
                    error(f"OpenAIError thrown: {e}")
                    errors += 1

        output_file.write(f"Total queries = {count}, errors = {errors}\n")

    if errors > 0:
        error(f'"{label}" run had errors.')

def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model", help=f"Use MODEL as the inference model. Default: {default_model}")
    parser.add_argument("-s", "--service-url", help=f"Use SERVICE_URL as the inference hosting service URL. Default: {default_service_url}")
    parser.add_argument("-t", "--template-dir", help=f"Use TEMPLATE_DIR as the location to find the prompt templates used. Default: {default_template_dir}")
    parser.add_argument("-o", "--output", help="Where standard output is written. Defaults to stdout.")
    args = parser.parse_args()

    model_name = args.model if args.model else default_model
    service_url = args.service_url if args.service_url else default_service_url
    template_dir = args.template_dir if args.template_dir else default_template_dir
    output_file = sys.stdout
    output_file_msg = 'stdout'
    if args.output:
        output_file = open(args.output, "w") 
        output_file_msg = args.output 
    print(f"""
{sys.argv[0]}:
  Model:        {model_name}
  Service URL:  {service_url}
  Template dir: {template_dir}
  Output:       {output_file_msg}
""")

    trial(output_file, service_url, template_dir, "refill", refill_expected_response, refill_queries, template_names, drugs, model_name)
    trial(output_file, service_url, template_dir, "non-refill", other_query_expected_response, other_queries, template_names, drugs, model_name)

if __name__ == "__main__":
    main()
