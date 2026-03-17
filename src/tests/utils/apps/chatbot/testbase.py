# Common code for tests of the "ChatBot" module using Hypothesis for property-based testing.
# https://hypothesis.readthedocs.io/en/latest/

from hypothesis import given, strategies as st

import json, logging, os, random, re, sys, unittest
from datetime import datetime
from io import StringIO
from pathlib import Path

from apps.chatbot import ChatBot, ChatBotResponseHandler, ChatBotShell
from common.utils import parse_json
from common.collections import dict_permutations

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

    def dict(self) -> dict[str,any]:
        d = {
            'name': 'TestPrompt',
        }
        d.update(vars(self))
        return d

    def json(self) -> str:
        return json.dumps(self.dict())

class LowConfidenceResult():
    """
    Hold a _low confidence result_, i.e., when the prompt has been rated below `rating_threshold`, or the returned
    answer has confidence below `confidence_threshold`, or both, in which case we can't trust that the returned answer
    should be exactly as expected.
    """        
    def __init__(self, query: str, reply: dict[str,any], test_prompt: TestPrompt, rating_threshold: int, confidence_threshold: float):
        self.query = query
        self.reply = reply
        self.test_prompt = test_prompt
        self.rating_threshold = rating_threshold
        self.confidence_threshold = confidence_threshold
    
    def __repr__(self) -> str:
        return f"""LowConfidenceResult(query='{self.query}',reply='{self.reply}',test_prompt='{self.test_prompt}',rating_threshold='{self.rating_threshold}',confidence_threshold={self.confidence_threshold})"""

    def dict(self) -> dict[str,any]:
        # We don't use __dict__ here because we need to turn the TestPrompt instance into a dictionary.
        # TODO: Is there a more standard way to make any class recursively convertible to a dictionary?
        return {
            'name':                  'LowConfidenceResult',
            'query':                 self.query,
            'reply':                 self.reply,
            'test_prompt':           self.test_prompt.dict(),
            'rating_threshold':      self.rating_threshold,
            'confidence_threshold':  self.confidence_threshold,
        }

    def json(self) -> str:
        return json.dumps(self.dict())

class TestBase(unittest.TestCase):
    """
    Base class for ChatBot tests. This class implements a number of extensions to normal 
    TestCase behavior, which we added to address some of the challenges of testing stochastic
    AI behaviors. The features include the following:
    
    * A _confidence threshold_:
        * Minimal testing is done on a response if the confidence score included in the
        response is below a threshold.
    * A _rating threshold_:
        * Similarly, if the generated Q&A pair was validated below a threshold, we don't
        require testing with it to "pass".
    * A flag for _testing all examples_ or not and a _sampling rate_:
        * Running with all the test Q&A pairs and some variable substitutions supported
        takes a very long time, so we support sampling a subset for faster unit test runs.
    * Accumulating all errors vs. failing fast:
        We have found it useful to accumulate and report all found errors vs. the normal
        approach of failing fast on the first error.
    """
    default_confidence_threshold = ChatBot.default_confidence_threshold
    default_rating_threshold = 4
    total_error_count = 0
    log_file_name = ''
    log_file = None

    def make_chatbot(self):
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.INFO)
        self.chatbot = ChatBot(
            model = self.model,
            service_url = self.service_url,
            template_dir = self.template_dir,
            data_dir = self.data_dir,
            confidence_level_threshold = self.confidence_threshold,
            logger = logger)
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
        self.data_dir                     = os.environ.get('DATA_DIR', 'data')
        self.test_all_examples: bool      = bool(os.environ.get('TEST_ALL_EXAMPLES', False))
        self.sample_rate: float           = float(os.environ.get('DATA_SAMPLE_RATE', 1.0))
        self.rating_threshold: int        = int(os.environ.get('RATING_THRESHOLD', self.default_rating_threshold))
        self.confidence_threshold: float  = float(os.environ.get('CONFIDENCE_THRESHOLD', self.default_confidence_threshold))
        self.verbose: bool                = bool(os.environ.get('VERBOSE', False))
        if self.test_all_examples:
            self.sample_rate = 1.0

        self.low_confidence_results = []
        self.errors = []
        self.samples_count: int = 0

        self.make_chatbot()

        d = {
            'step' :                        'setUp',
            'model':                        self.model,
            'service_url':                  self.service_url,
            'template_dir':                 self.template_dir,
            'data_dir':                     self.data_dir,
            'test_all_examples':            self.test_all_examples,
            'default sample_rate':          self.sample_rate,
            'default rating_threshold':     self.rating_threshold,
            'default confidence_threshold': self.confidence_threshold,
        }
        print(json.dumps(d), file=TestBase.log_file)

    def tearDown(self):
        TestBase.total_error_count += len(self.errors)
        lcrs = [lcr.dict() for lcr in self.low_confidence_results]
        d = {
            'step':              'tearDown',
            'samples_count':     self.samples_count,
            'low_confidence_results': {
                'count':         len(self.low_confidence_results),
                'results':       lcrs,
            },
            'errors': {
                'count':         len(self.errors),
                'errors':        self.errors,
            },
        }
        js1 = json.dumps(d)
        js  = re.sub(r'\n', r'\\n', js1)  # Try to print true JSONL records
        print(js, file=TestBase.log_file)
        if not self.samples_count:
            raise ValueError(f"No samples were loaded!")            

    @classmethod
    def setUpClass(cls):
        log_dir = "tests/logs"
        TestBase.log_file_name = f"{log_dir}/{cls.__name__}-{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        print(f"Logging to {TestBase.log_file_name}")
        os.makedirs(log_dir, exist_ok=True)
        TestBase.log_file = open(TestBase.log_file_name, 'w')

    @classmethod
    def tearDownClass(cls):
        if TestBase.total_error_count:
            raise AssertionError(f"{TestBase.total_error_count} errors occurred!")

    def load_test_data(self, path: Path) -> [TestPrompt]:
        if not path.exists():
            raise FileNotFoundError(path)

        prompts = []
        with path.open('r') as file:
            for line in file:
                try:
                    obj     = parse_json(line)
                    query   = obj.get('query')
                    label   = obj.get('label')
                    actions = obj.get('actions')
                    rating  = obj.get('rating')
                    tp = TestPrompt(query, label, actions, rating)
                    prompts.append(tp)
                except ValueError as err:
                    raise ValueError(f"From file {file}, error parsing line: {line}") from err
        if not len(prompts):
            raise ValueError(f"No prompts were loaded from {file}!")
        return prompts

    def try_query(self, 
        test_prompt: TestPrompt,
        place_holders: dict[str,str],
        allowed_alt_labels: dict[str,[str]],
        rating_threshold: int = default_rating_threshold,
        confidence_threshold: float = default_confidence_threshold):
        """
        See src/apps/prompts/templates/patient-chatbot.yaml for "requirements".
        Compare to `try_query_accumulate()`.
        We don't check the text returned. For a few labels, we don't use that text,
        but for other labels, we would show the text to the user. We could enhance
        these tests to use an LLM as a judge to decide on the quality of the returned
        texts, at the expense of additional overhead for the inference required.
        """
        exp_query   = test_prompt.query
        exp_label   = test_prompt.label
        exp_actions = test_prompt.actions
        exp_rating  = test_prompt.rating
        prompt      = exp_query.format_map(place_holders)
        
        answer = self.chatbot.query(prompt)
        self.assertFalse(isinstance(answer, str), f"Error message returned: {answer}")
        actual_query1        = answer.get('query')
        actual_content       = answer.get('content')
        actual_rtu           = answer.get('reply_to_user')
        actual_query2        = actual_content.get('query')
        actual_reply         = actual_content.get('reply')
        actual_label         = actual_reply.get('label')
        actual_actions       = actual_reply.get('actions', '')
        actual_confidence    = actual_reply.get('confidence', 0.0)
        # actual_text          = actual_reply.get('text', '')

        err_msg = str(answer)
        self.assertEqual(prompt, actual_query1, err_msg)
        self.assertEqual(prompt, actual_query2, err_msg)

        if actual_confidence < confidence_threshold:
            self.assertEqual('other', actual_label, f"label: other != {actual_label}, error_msg = {err_msg}")
            exp_rtu = ChatBotResponseHandler.replies['other']
            self.assertEqual(exp_rtu, actual_rtu, f"reply_to_user: <{exp_rtu}> != <{actual_rtu}>, error_msg = {err_msg}")
        elif exp_rating < rating_threshold:
            self.low_confidence_results.append(LowConfidenceResult(
                prompt, actual_reply, test_prompt, rating_threshold, confidence_threshold))
        else:
            err_msg = self._check_label(exp_label, actual_label, allowed_alt_labels)
            self.assertEqual(0, len(err_msg), err_msg)
            if actual_label == 'emergency' or actual_label == 'other':
                # Ignore the action if we detect an emergency or other prompt, but check
                # the returned user response, since we always return with the same reply for 
                # these labels!
                exp_rtu = ChatBotResponseHandler.replies[actual_label]
                self.assertEqual(exp_rtu, actual_rtu, f"reply_to_user: <{exp_rtu}> != <{actual_rtu}>, error_msg = {err_msg}")
            else:
                # Do the actions match for the other label cases? Note that the ChatBot could return
                # more than one, a comma-separated list, so we just check if the one or more expected
                # actions are present.
                for action in exp_actions.split(','):
                    a = action.strip()
                    self.assertTrue(actual_actions.find(a) > 0, f"""expected action "{a}" not found in != "{actual_actions}", exp_actions = "{exp_actions}", error_msg = {err_msg}""")

            # For the "place holders", ignore case, since sometimes proper names,
            # like for pharmaceuticals, can occur with different cases. Also, we
            # check that _expected_ values, if any are present, but also allow for
            # additional actual values. This is because some of the test queries
            # hard-code body parts and pharmaceuticals and don't always use the "{foo}"
            # convention for such things.
            for key in place_holders:
                expected = place_holders.get(key).lower()
                actual   = actual_reply.get(key).lower()
                self.assertTrue(actual.find(expected) >= 0, f"""for key = "{key}": expected = "{expected}", actual = "{actual}", {err_msg}""")

    def try_query_accumulate(self, 
        test_prompt: TestPrompt,
        place_holders: dict[str,str],
        allowed_alt_labels: dict[str,[str]],
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
        prompt      = exp_query.format_map(place_holders)
        
        errors_metadata = {
            'prompt': prompt,
            'test_prompt': test_prompt.dict(),
            'place_holders': place_holders,
            'rating_threshold': rating_threshold,
            'confidence_threshold': confidence_threshold,
        }
        # On success this will be returned as empty. If problems are found,
        # we put those kvs first, so they are printed first...
        errors = {}

        answer = self.chatbot.query(prompt)
        if isinstance(answer, str):
            return {
                'query_failure': f"Error message returned: {answer}",
                'metadata':      errors_metadata,
            }
        else:
            errors_metadata['answer'] = answer

        actual_query1        = answer.get('query')
        actual_rtu           = answer.get('reply_to_user')
        actual_content       = answer.get('content')
        actual_query2        = actual_content.get('query')
        actual_reply         = actual_content.get('reply')
        actual_label         = actual_reply.get('label')
        actual_actions       = actual_reply.get('actions', '')
        actual_confidence    = actual_reply.get('confidence', 0.0)
        # actual_text          = actual_reply.get('text', '')

        if prompt != actual_query1:
            errors['answer.query'] = f"{prompt} != {actual_query1}"
        if prompt != actual_query2:
            errors['content.query'] = f"{prompt} != {actual_query2}"
        
        if actual_confidence < confidence_threshold:
            if 'other' != actual_label:
                errors['label'] = f"other != {actual_label}"
            else:
                exp_rtu = ChatBotResponseHandler.replies['other']
                if exp_rtu != actual_rtu:
                    errors['reply_to_user'] = f"<{exp_rtu}> != <{actual_rtu}>"
        elif exp_rating < rating_threshold:
            self.low_confidence_results.append(LowConfidenceResult(
                prompt, actual_reply, test_prompt, rating_threshold, confidence_threshold))
        else:
            err_msg = self._check_label(exp_label, actual_label, allowed_alt_labels)
            if len(err_msg) > 0:
                errors['label'] = err_msg
            if actual_label == 'emergency' or actual_label == 'other':
                # Ignore the action if we detect an emergency or other prompt, but check
                # the returned user response, since we always return with the same reply for 
                # these labels!
                exp_rtu = ChatBotResponseHandler.replies[actual_label]
                if exp_rtu != actual_rtu:
                    errors['reply_to_user'] = f"<{exp_rtu}> != <{actual_rtu}>"
            else:
                # Do the actions match for the other label cases? Note that the ChatBot could return
                # more than one, a comma-separated list, so we just check if the one or more expected
                # actions are present.
                missing_actions = []
                for action in exp_actions.split(','):
                    a = action.strip()
                    if actual_actions.find(a) < 0:
                        missing_actions.append(a)
                if missing_actions:
                    errors['actions'] = f"""some expected actions "{missing_actions}" (out of "{exp_actions}") not found in the actual actions "{actual_actions}"."""

            # For the "place holders", ignore case, since sometimes proper names,
            # like for pharmaceuticals, can occur with different cases. Also, we
            # check that _expected_ values, if any are present, but also allow for
            # additional actual values. This is because some of the test queries
            # hard-code body parts and pharmaceuticals and don't always use the "{foo}"
            # convention for such things.
            missing_phs = {}
            for key in place_holders:
                expected = place_holders.get(key).lower()
                actual   = actual_reply.get(key).lower()
                if not actual.find(expected) >= 0:
                    missing_phs['key'] = f"{expected} vs. {actual}"
            if missing_phs:
                errors['place_holder'] = missing_phs

        if errors:
            errors['metadata'] = errors_metadata
        return errors

    def try_queries(self, 
        file_name: Path | str, 
        place_holders: dict[str,[str]], 
        allowed_alt_labels: dict[str,[str]],
        sample_rate: float = None, 
        rating_threshold: int = default_rating_threshold,
        confidence_threshold: float = default_confidence_threshold,
        accumulate_errors: bool = True):
        if self.test_all_examples:   # Override based on env. var.?
            sample_rate = 1.0
        elif not sample_rate:
            sample_rate = self.sample_rate

        d = {
            'step':                  'try_queries',
            'file_name':             str(file_name),
            'sample_rate':           sample_rate,
            'rating_threshold':      rating_threshold,
            'confidence_threshold':  confidence_threshold,
            'place_holders':         place_holders,
        }
        print(json.dumps(d), file=TestBase.log_file)

        test_prompts = self.load_test_data(Path(file_name))
        samples = self._sample(test_prompts, sample_rate) if sample_rate < 1.0 else test_prompts
        self.samples_count += len(samples)

        # Start by determining if the prompt contains any of the placeholders. If a place holder
        # key is found in place_holders, then we will iterate through the list of them. If not
        # found we will skip that key:[str] pair.
        phs = {}
        for test_prompt in samples:
            for key in place_holders:
                if test_prompt.query.find('{'+key+'}') >= 0:
                    phs[key] = place_holders[key]

            # Now create the key-value pairs from phs:
            n = 1 if self.test_all_examples else -1
            all_ph_pairs = dict_permutations(phs, max_size=n)
            for ph_pairs in all_ph_pairs:
                if accumulate_errors:
                    errs = self.try_query_accumulate(test_prompt, ph_pairs, allowed_alt_labels,
                        rating_threshold=rating_threshold, 
                        confidence_threshold=confidence_threshold)
                    if errs:
                        self.errors.append(errs)
                else:
                    self.try_query(test_prompt, ph_pairs, allowed_alt_labels,
                        rating_threshold=rating_threshold, 
                        confidence_threshold=confidence_threshold)

    def _sample(self, collection: list[any], sample_rate: float) -> list[any]:
        """
        The sample_rate (between 0.0 and 1.0) is a pragmatic compromise due to relatively slow local inference
        and expensive inference services. Use a low value for unit tests that are run frequently and need to be fast.
        Use a high value for integration and acceptance tests, usually 1.0, to run most or all of the available test
        prompts, for more exhaustive coverage. However, if the sampled number of test prompts will be less than 5
        (arbitrary), we run the first five available (if the collection has that many...).
        """
        minimum_n = 5
        n = len(collection)
        self.assertTrue(n > 0, f"Collection has no elements! {collection}")
        samples = collection
        if n > minimum_n and sample_rate < 1.0:
            # The samples will be unsorted, but that's okay, as we would like to catch subtle differences
            # in behavior that might be triggered by different ordering.
            k = round(sample_rate * n)
            if k < minimum_n:
                k = minimum_n
            samples = random.sample(collection, k=k)
        return samples

    def _check_label(self, expected: str, actual: str, allowed_alt_labels: dict[str,[str]]) -> str:
        if expected == actual:
            return ""
        
        alts = allowed_alt_labels.get(expected)
        for alt in alts:
            if expected == alt:
                return ""
        return f"{expected} != {actual} and the latter is not allowed as an alternate for the expected label: {alts}"
