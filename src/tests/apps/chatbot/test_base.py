# Common code for tests of the "ChatBot" module using Hypothesis for property-based testing.
# https://hypothesis.readthedocs.io/en/latest/

from hypothesis import given, strategies as st

import json, os, random, re, sys, unittest
from io import StringIO
from pathlib import Path
from rich import print as rprint

from apps.chatbot import ChatBot, ChatBotResponseHandler, ChatBotShell
from common.utils import parse_json
    
class TestPrompt():
    """Class to hold a benchmark datum: a prompt and expected label, actions, and rating."""
    def __init__(self,
        query: str,
        label: str,
        actions: str,
        rating: int):
        self.query = query
        self.label = label
        self.actions = actions
        self.rating = rating
        errors = []
        if not self.query:
            errors.append('empty query')
        if not self.label:
            errors.append('empty label')
        if rating < 0 or rating > 5:
            errors.append(f'invalid rating {self.rating} (not between 0 and 5, inclusive)')
        if errors:
            raise ValueError(f"Invalid inputs: {', '.join(errors)}")

    def __repr__(self) -> str:
        return f"""TestPrompt(query='{self.query}',label='{self.label}',actions='{self.actions}',rating={self.rating})"""

class LowConfidenceResult():
    """
    Hold a _low confidence result_, i.e., when the prompt has been rated below `rating_threshold`, or the returned
    answer has confidence below `confidence_threshold`, or both, in which case we can't trust that the returned answer
    should be exactly as expected.
    """        
    def __init__(self, reply: dict[str,any], test_prompt: TestPrompt, rating_threshold: int, confidence_threshold: float):
        self.reply = reply
        self.test_prompt = test_prompt
        self.rating_threshold = rating_threshold
        self.confidence_threshold = confidence_threshold
    
    def __repr__(self) -> str:
        return f"""LowConfidenceResult(reply='{self.reply}',test_prompt='{self.test_prompt}',rating_threshold='{self.rating_threshold}',confidence_threshold={self.confidence_threshold})"""

class TestBase(unittest.TestCase):
    """
    Base class for ChatBot tests.
    """

    default_confidence_threshold = ChatBot.default_confidence_threshold
    default_rating_threshold = 4

    place_holders = {
        'prescriptions': ['prilosec', 'xanax'],
        'body_parts': ['stomach', 'heart'],
    }

    def make_chatbot(self):
        self.chatbot = ChatBot(
            model = self.model,
            service_url = self.service_url,
            template_dir = self.template_dir)
        self.shell = ChatBotShell(self.chatbot, stdout = StringIO())

    def setUp(self):
        """
        Initialize the ChatBot and ChatBotShell. Track the number of confident and "low-confidence" results.
        By default, all test data prompts are executed, which can be too slow and expensive for frequent 
        unit tests. Override the environment variable `DATA_SAMPLE_RATE` when invoking tests with a value
        between 0.0 (none) and 1.0 (all) to control the amount of test data prompts sampled. (A minimum 
        threshold of 5 samples, if available, will be used in all cases.)
        """
        self.model                        = os.environ.get('MODEL', 'ollama_chat/gpt-oss:20b')
        self.service_url                  = os.environ.get('INFERENCE_URL', 'http://localhost:11434')
        self.template_dir                 = os.environ.get('PROMPTS_TEMPLATES_DIR', 'prompts/templates')
        self.sample_rate: float           = float(os.environ.get('DATA_SAMPLE_RATE', 1.0))
        self.test_all_examples: bool      = bool(os.environ.get('TEST_ALL_EXAMPLES', False))
        self.rating_threshold: int        = int(os.environ.get('RATING_THRESHOLD', self.default_rating_threshold))
        self.confidence_threshold: float  = float(os.environ.get('CONFIDENCE_THRESHOLD', self.default_confidence_threshold))

        self.verbose: bool            = bool(os.environ.get('VERBOSE', False))
        if self.verbose:
            rprint()
            rprint(f"model:                {self.model}")
            rprint(f"service_url:          {self.service_url}")
            rprint(f"template_dir:         {self.template_dir}")
            rprint(f"sample_rate:          {self.sample_rate}")
            rprint(f"test_all_examples:    {self.test_all_examples}")
            rprint(f"rating_threshold:     {self.rating_threshold}")
            rprint(f"confidence_threshold: {self.confidence_threshold}")

        self.low_confidence_results = []
        self.errors = {}
        self.samples_count: int = 0
        self.make_chatbot()

    def tearDown(self):
        if self.low_confidence_results:
            rprint()
            ratio = f"{len(self.low_confidence_results)}/{self.samples_count}"
            rprint(f"{__file__}: Minimal checking was done on the following {ratio} 'low-confidence results':")
            for lcr in self.low_confidence_results:
                rprint(lcr)
            rprint()
        if self.errors:
            rprint("Accumulated errors!")
            for prompt, error in self.errors.items():
                rprint(f"prompt = {prompt}:")
                rprint(f"error(s) = {error}\n")
            self.fail(f"{len(self.errors)} found!")

    def load_test_data(self, path: Path) -> [TestPrompt]:
        if not path.exists():
            raise FileNotFoundError(path)

        prompts = []
        with path.open('r') as file:
            for line in file:
                obj     = parse_json(line)
                query   = obj.get('query')
                label   = obj.get('label')
                actions = obj.get('actions')
                rating  = obj.get('rating')
                tp = TestPrompt(query, label, actions, rating)
                prompts.append(tp)
        if not len(prompts):
            raise ValueError(f"No prompts were loaded from {file}!")
        return prompts

    def try_query(self, 
        test_prompt: TestPrompt,
        place_holders: dict[str,str],
        rating_threshold: int = default_rating_threshold,
        confidence_threshold: float = default_confidence_threshold):
        """
        See src/apps/prompts/templates/patient-chatbot.yaml for "requirements".
        Compare to `try_query_accumulate()`.
        """
        exp_query   = test_prompt.query
        exp_label   = test_prompt.label
        exp_actions = test_prompt.actions
        exp_rating  = test_prompt.rating
        exp_place_holders = {}
        for key, value in place_holders.items():
            exp_place_holders[key] = value if exp_query.find('{'+key+'}') >= 0 else ''
        prompt = exp_query.format_map(exp_place_holders)
        
        answer = self.chatbot.query(prompt)
        self.assertFalse(isinstance(answer, str), f"Error message returned: {answer}")
        actual_query1        = answer.get('query')
        actual_content       = answer.get('content')
        actual_query2        = actual_content.get('query')
        actual_reply         = actual_content.get('reply')
        actual_label         = actual_reply.get('label')
        actual_prescriptions = actual_reply.get('prescriptions', '')
        actual_body_parts    = actual_reply.get('body_parts', '')
        actual_actions       = actual_reply.get('actions', '')
        actual_confidence    = actual_reply.get('confidence', 0.0)
        actual_text          = actual_reply.get('text', '')

        err_msg = str(answer)
        self.assertEqual(prompt, actual_query1, err_msg)
        self.assertEqual(prompt, actual_query2, err_msg)
        if actual_confidence >= confidence_threshold and exp_rating >= rating_threshold:
            self.assertEqual(exp_label,   actual_label,   err_msg)
            if exp_label == 'emergency' or exp_label == 'other':
                # Ignore the action if we detect an emergency or other prompt, but check
                # the returned text, since we always return with the same reply for these labels!
                exp_text = ChatBotResponseHandler.replies[exp_label]
                self.assertEqual(exp_text, actual_text, err_msg)
            else:
                # Do the actions match for the other label cases?
                self.assertEqual(exp_actions, actual_actions, err_msg)

            # For the "place holders", ignore case, since sometimes proper names,
            # like for pharmaceuticals, can occur with different cases. Also, we
            # check that _expected_ values, if any are present, but also allow for
            # additional actual values. This is because some of the test queries
            # hard-code body parts and pharmaceuticals and don't always use the "{foo}"
            # convention for such things.
            for key in exp_place_holders:
                expected = exp_place_holders.get(key).lower()
                actual   = actual_reply.get(key).lower()
                self.assertTrue(actual.find(expected) >= 0, f"for key = {key}: expected = {expected}, actual = {actual}, {err_msg}")
        else:
            self.low_confidence_results.append(LowConfidenceResult(actual_reply, test_prompt, rating_threshold, confidence_threshold))
    

    def try_query_accumulate(self, 
        test_prompt: TestPrompt,
        place_holders: dict[str,str],
        rating_threshold: int = default_rating_threshold,
        confidence_threshold: float = default_confidence_threshold) -> dict[str,any]:
        """
        See src/apps/prompts/templates/patient-chatbot.yaml for "requirements".
        Rather than follow the usual approach for failing fast on the first wrong datum, 
        we run all the examples and accumulate error messages, then report the results.
        Compare to `try_query()`.
        """
        exp_query   = test_prompt.query
        exp_label   = test_prompt.label
        exp_actions = test_prompt.actions
        exp_rating  = test_prompt.rating
        exp_place_holders = {}
        for key, value in place_holders.items():
            exp_place_holders[key] = value if exp_query.find('{'+key+'}') >= 0 else ''
        prompt = exp_query.format_map(exp_place_holders)
        
        answer = self.chatbot.query(prompt)
        self.assertFalse(isinstance(answer, str), f"Error message returned: {answer}")
        actual_query1        = answer.get('query')
        actual_content       = answer.get('content')
        actual_query2        = actual_content.get('query')
        actual_reply         = actual_content.get('reply')
        actual_label         = actual_reply.get('label')
        actual_prescriptions = actual_reply.get('prescriptions', '')
        actual_body_parts    = actual_reply.get('body_parts', '')
        actual_actions       = actual_reply.get('actions', '')
        actual_confidence    = actual_reply.get('confidence', 0.0)
        actual_text          = actual_reply.get('text', '')

        errors = {}
        if prompt != actual_query1:
            errors['answer.query'] = f"query: {prompt} != {actual_query1}"
        if prompt != actual_query2:
            errors['content.query'] = f"query: {prompt} != {actual_query2}"
        if actual_confidence < confidence_threshold:
            if 'other' != actual_label:
                errors['label'] = f"label: other != {actual_label}"
            else:
                exp_text = ChatBotResponseHandler.replies[exp_label]
                if exp_text != actual_text:
                    errors['text'] = f"text: {exp_text} != {actual_text}"
        elif exp_rating < rating_threshold:
            self.low_confidence_results.append(LowConfidenceResult(actual_reply, test_prompt, rating_threshold, confidence_threshold))
        else:
            if exp_label != actual_label:
                errors['label'] = f"label: {exp_label} != {actual_label}"
            if exp_label == 'emergency' or exp_label == 'other':
                # Ignore the action if we detect an emergency or other prompt, but check
                # the returned text, since we always return with the same reply for these labels!
                exp_text = ChatBotResponseHandler.replies[exp_label]
                if exp_text != actual_text:
                    errors['text'] = f"text: {exp_text} != {actual_text}"
            else:
                # Do the actions match for the other label cases?
                if exp_actions != actual_actions:
                    errors['actions'] = f"actions: {exp_actions} != {actual_actions}"
            # For the "place holders", ignore case, since sometimes proper names,
            # like for pharmaceuticals, can occur with different cases. Also, we
            # check that _expected_ values, if any are present, but also allow for
            # additional actual values. This is because some of the test queries
            # hard-code body parts and pharmaceuticals and don't always use the "{foo}"
            # convention for such things.
            for key in exp_place_holders:
                expected = exp_place_holders.get(key).lower()
                actual   = actual_reply.get(key).lower()
                if not actual.find(expected) >= 0:
                    errors[key] = f"key = {key}: {expected} vs. {actual}"

        if errors:
            errors['answer'] = answer
        return errors

    def _sample(self, collection: list[any], sample_rate: float) -> list[any]:
        """
        The sample_rate (between 0.0 and 1.0) is a pragmatic compromise due to relatively slow local inference
        and expensive inference services. Use a low value for unit tests that are run frequently and need to be fast.
        Use a high value for integration and acceptance tests, usually 1.0, to run most or all of the available test
        prompts, for more exhaustive coverage. However, if the total number of test prompts is less than 5 (arbitrary),
        we run all of them, for any sample_rate > 0.
        """
        if not sample_rate:
            sample_rate = self.sample_rate        
        minimum_n = 5
        n = len(collection)
        samples = collection
        if sample_rate <= 0.0 or n <= minimum_n:
            samples = collection[0:minimum_n]
        elif sample_rate < 1.0:
            # The samples will be unsorted, but that's okay, as we would like to catch subtle differences
            # in behavior that might be triggered by different ordering.
            k = int(sample_rate * n) if n > minimum_n else minimum_n
            samples = random.sample(collection, k=k)
        return samples

    def try_queries(self, 
        file_name: str, 
        place_holders: dict[str,str], 
        sample_rate: float = None, 
        rating_threshold: int = default_rating_threshold,
        confidence_threshold: float = default_confidence_threshold):
        if self.test_all_examples:
            self.__try_all_queries(file_name, place_holders, 
                sample_rate=sample_rate, rating_threshold=rating_threshold, confidence_threshold=confidence_threshold)
        else:
            self.__try_queries(file_name, place_holders, 
                sample_rate=sample_rate, rating_threshold=rating_threshold, confidence_threshold=confidence_threshold)

    def __try_queries(self,
        file_name: str, 
        place_holders: dict[str,str], 
        sample_rate: float = None, 
        rating_threshold: int = default_rating_threshold,
        confidence_threshold: float = default_confidence_threshold):
        test_prompts = self.load_test_data(Path(file_name))
        samples = self._sample(test_prompts, sample_rate)
        self.samples_count = len(samples)
        for test_prompt in samples:
            self.try_query(test_prompt, place_holders, 
                rating_threshold=rating_threshold, confidence_threshold=confidence_threshold)

    def __try_all_queries(self,
        file_name: str, 
        place_holders: dict[str,str], 
        sample_rate: float = None, 
        rating_threshold: int = default_rating_threshold,
        confidence_threshold: float = default_confidence_threshold):
        test_prompts = self.load_test_data(Path(file_name))
        samples = self._sample(test_prompts, sample_rate)
        self.samples_count = len(samples)
        for test_prompt in samples:
            errs = self.try_query_accumulate(test_prompt, place_holders, 
                rating_threshold=rating_threshold, confidence_threshold=confidence_threshold)
            if errs:
                self.errors[test_prompt] = errs

