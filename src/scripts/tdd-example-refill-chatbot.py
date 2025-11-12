import os
import sys
from pathlib import Path
import logging
import Levenshtein
from litellm import completion
from openai import OpenAIError
from utils import setup, load_yaml, make_full_prompt, extract_content, not_none

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

    def __init__(self, model_name: str, lev_threshold: float, service_url: str, template_dir: str, logger: logging.Logger):
        self.model_name    = model_name
        self.lev_threshold = lev_threshold
        self.service_url   = service_url
        self.template_dir  = template_dir
        self.logger        = logger

    def trial(self, label):
        """Performs trials for the given label and queries."""
        count = 0
        errors = 0
        self.logger.info(f"Queries that are {label} requests:")
        self.logger.info("Comparisons ignore case, remove leading '-', and '*' around words (Markdown-style formatting).")
        self.logger.info(f"Levenshtein ratio used, with values above {self.lev_threshold} interpreted as 'equal'.")

        not_none(self.queries_responses[label], f'No queries and expected responses are known for key {label}.')

        queries = self.queries_responses[label]['queries']
        expected_response = self.queries_responses[label]['expected_response']
        not_none(queries, f'No queries are known for key {label}.')
        not_none(expected_response, f'No expected responses are known for key {label}.')
        
        for template_name in self.template_names:
            self.logger.info(f"  Using template {template_name} in {self.template_dir}:")
            template = load_yaml(Path(self.template_dir, template_name+".yaml"))

            for query in queries:
                for drug in self.drugs:
                    expected = expected_response.replace("_P_", drug)
                    expected_lc = expected.lower()
                    query_with_drug = query.replace("_P_", drug)

                    try:
                        response = completion(
                            model = self.model_name, 
                            messages = [{ 
                                "content": make_full_prompt(query_with_drug, template['system']),
                                "role": "user",
                            }], 
                            api_base = self.service_url, 
                            stream = False,
                            verbose = False,
                        )
                        count += 1
                        actual = extract_content(response)
                        prefix_str = f"    Query: {query_with_drug} => "
                        if actual == expected:
                            self.logger.info(f"{prefix_str} SUCCESS! (strings identical, actual = expected = \"{expected}\")")
                        elif actual != expected:
                            actual_lc = actual.lower().strip()
                            # Remove leading `-` if present. Remove "*" around words.
                            actual_lc = actual_lc.lstrip("-").replace('*', '')
                            ratio = Levenshtein.ratio(actual_lc, expected_lc)
                            if ratio >= self.lev_threshold:
                                self.logger.info(f"{prefix_str} SUCCESS! (leading '-' and all '*' removed, Lev. distance ratio {ratio} >= {self.lev_threshold}: actual = \"{actual}\", expected = \"{expected}\")")
                            else:
                                errors += 1
                                resp_str = f"Lev. ratio = {ratio} > {self.lev_threshold}, actual = \"{actual}\", expected = \"{expected}\" (full response: \"{response}\")"
                                self.logger.warning(f"{prefix_str} FAILURE! ({resp_str})")

                    except OpenAIError as e:
                        self.logger.error(f"OpenAIError thrown: {e}")
                        sys.exit(1)

            self.logger.info(f"Total queries = {count}, errors = {errors}")

        if errors > 0:
            self.logger.warning(f'"{label}" run had errors, but we will continue running.')

def main():

    script = os.path.basename(__file__)
    description = "TDD Example 'refill' use case for the healthcare ChatBot."
    epilog = "NOTE: the --data-dir argument is currently ignored!"
    args, logger = setup(script, description, epilog = epilog,
        add_arguments = lambda p: p.add_argument("--lev-threshold", 
            default=common_defaults['levenshtein-ratio-threshold'], 
            help=f"The threshold between 0.0 and 1.0, inclusive, above which we consider two strings identical based on the 'Levenshtein distance'. Default: {common_defaults['levenshtein-ratio-threshold']}"))

    if args.lev_threshold < 0.0 or args.lev_threshold > 1.0:
        logger.error(f"The Levenshtein ratio threshold must be between 0.0 and 1.0, inclusive: {args.lev_threshold}")
        sys.exit(1)

    logger.info(f"{script}:")
    logger.info(f"  Model:                        {args.model}")
    logger.info(f"  Levenshtein ratio threshold:  {args.lev_threshold}")
    logger.info(f"  Service URL:                  {args.service_url}")
    logger.info(f"  Template dir:                 {args.template_dir}")
    logger.info(f"  Log:                          {args.log}")

    tdd = TDDExampleRefillChatbot(args.model, args.lev_threshold, args.service_url, args.template_dir, logger)
    tdd.trial("refill",)
    tdd.trial("non-refill")

if __name__ == "__main__":
    main()
