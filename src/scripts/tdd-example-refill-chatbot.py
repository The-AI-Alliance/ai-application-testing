import sys
from pathlib import Path
import logging
from litellm import completion
from openai import OpenAIError
from utils import load_yaml, make_full_prompt, extract_content
from utils import (
    get_default_log_file, make_logger, 
    load_yaml, make_full_prompt, extract_content
)

class TDDExampleRefillChatbot:

    queries_responses = {
        "refill": {
            "queries": [
                "I need my _P_ refilled.",
                "I need my _P_ drug refilled.",
                "I'm out of _P_. Can I get a refill?",
                "I need more _P_.",
                "My pharmacy says I don't have any refills for _P_. Can you ask them to refill it?"
            ],
            "expected_response": "Okay, I have your request for a refill for _P_. I will check your records and get back to you within the next business day."
        },
        "non-refill": {
            "queries": [
                "My prescription for _P_ upsets my stomach.",
                "I have trouble sleeping, ever since I started taking _P_.",
                "When is my next appointment?"
            ],
            "expected_response": "I have received your message, but I can't answer it right now. I will get back to you within the next business day."
        }
    }

    template_names = [
        "q-and-a_patient-chatbot-prescriptions-with-examples",
        "q-and-a_patient-chatbot-prescriptions"
    ]

    drugs = [
        "prozac",
        "xanax"
    ]

    def __init__(self, model_name: str, service_url: str, template_dir: str, logger: logging.Logger):
        self.model_name   = model_name
        self.service_url  = service_url
        self.template_dir = template_dir
        self.logger       = logger

    def trial(self, label):
        """Performs trials for the given label and queries."""
        count = 0
        errors = 0
        self.logger.info(f"Queries that are {label} requests:")

        not_null(queries_responses[label], f'No queries and expected responses are known for key {label}.')

        queries = queries_responses[label]['queries']
        expected_response = queries_responses[label]['expected_response']
        not_null(queries, f'No queries are known for key {label}.')
        not_null(expected_responses, f'No expected responses are known for key {label}.')
        
        for template_name in template_names:
            self.logger.info(f"  Using template {template_name} in {self.template_dir}:")
            template = load_yaml(Path(self.template_dir, template_name+".yaml"))

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

                        self.logger.info(f"    Query: {query_with_drug} => {resp_str}")

                    except OpenAIError as e:
                        self.logger.error(f"OpenAIError thrown: {e}")
                        sys.exit(1)

            self.logger.info(f"Total queries = {count}, errors = {errors}")

        if errors > 0:
            self.logger.warning(f'"{label}" run had errors, but we will continue running.')

def main():
    """Main function."""
    import argparse

    default_model = "ollama/gpt-oss:20b"
    default_service_url = "http://localhost:11434"
    default_template_dir = "src/prompts/templates"
    default_data_dir = "data"

    script = os.path.basename(__file__)
    default_log_file = get_default_log_file(script)

    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model", default=default_model,
            help=f"Use MODEL as the inference model. Default: {default_model}")
    parser.add_argument("-s", "--service-url", default=default_service_url,
            help=f"Use SERVICE_URL as the inference hosting service URL. Default: {default_service_url}")
    parser.add_argument("-t", "--template-dir",  default=default_template_dir,
            help=f"Use TEMPLATE_DIR as the location to find the prompt templates used. Default: {default_template_dir}")
    parser.add_argument("-d", "--data-dir", default=default_data_dir,
            help=f"Directory where data files are written. IGNORED; NOT CURRENTLY USED! Default: {default_data_dir}")
    parser.add_argument("-o", "--output", default=default_log_file, 
            help=f"Where logging is written. Default: {default_log_file}.")
    args = parser.parse_args()

    logger = make_logger(args.output)
    print(f'Logging to {args.output}, level INFO')

    logger.info(f"{script}:")
    logger.info(f"  Model:        {args.model}")
    logger.info(f"  Service URL:  {args.service_url}")
    logger.info(f"  Template dir: {args.template_dir}")
    # logger.info(f"  Data dir:     {args.data_dir}")
    logger.info(f"  Log:          {args.output}")

    tdd = TDDExampleRefillChatbot(args.model, args.service_url, args.template_dir, logger)
    tdd.trial("refill",)
    tdd.trial("non-refill")

if __name__ == "__main__":
    main()
