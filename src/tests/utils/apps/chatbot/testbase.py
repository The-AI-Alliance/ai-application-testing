# Common code for tests of the "ChatBot" module using Hypothesis for property-based testing.
# https://hypothesis.readthedocs.io/en/latest/

from hypothesis import given, strategies as st

import json, logging, os, random, re, sys, time, unittest
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Any

from apps.chatbot import ChatBot, ChatBotResponseHandler, ChatBotShell
from common.utils import dict_pop, parse_json
from common.collections import dict_permutations

class TestPrompt():
    """Class to hold a benchmark datum: a prompt and expected labels, actions, and rating."""
    def __init__(self,
        query: str,
        labels: list[str],
        actions: list[str],
        rating: int,
        reason: str = '',
        keywords: dict[str,str] = {}):
        self.query = query
        self.labels = labels
        self.actions = actions
        self.rating = rating
        self.reason = reason if reason else ''
        self.keywords = keywords
        errors = []
        if not self.query:
            errors.append('empty query')
        if not self.labels:
            errors.append('empty labels')
        if rating < 0 or rating > 5:
            errors.append(f'invalid rating {self.rating} (not between 0 and 5, inclusive)')
        if errors:
            raise ValueError(f"Invalid inputs: {', '.join(errors)}")

    def __repr__(self) -> str:
        return f"""TestPrompt(query='{self.query}',labels='{self.labels}',actions='{self.actions}',rating={self.rating},reason={self.reason},keywords={self.keywords})"""

    def dict(self) -> dict[str,Any]:
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
    def __init__(self, 
        query: str, 
        reasons: str,
        reply: dict[str,Any], 
        test_prompt: TestPrompt, 
        rating_threshold: int, 
        confidence_threshold: float):
        self.query = query
        self.reasons = reasons
        self.reply = reply
        self.test_prompt = test_prompt
        self.rating_threshold = rating_threshold
        self.confidence_threshold = confidence_threshold
    
    def __repr__(self) -> str:
        return f"""LowConfidenceResult(query='{self.query}',reasons='{self.reasons}',reply='{self.reply}',test_prompt='{self.test_prompt}',rating_threshold='{self.rating_threshold}',confidence_threshold={self.confidence_threshold})"""

    def dict(self) -> dict[str,Any]:
        # We don't use __dict__ here because we need to turn the TestPrompt instance into a dictionary.
        # TODO: Is there a more standard way to make any class recursively convertible to a dictionary?
        return {
            'name':                  'LowConfidenceResult',
            'query':                 self.query,
            'reasons':               self.reasons,
            'reply':                 self.reply,
            'test_prompt':           self.test_prompt.dict(),
            'rating_threshold':      self.rating_threshold,
            'confidence_threshold':  self.confidence_threshold,
        }

    def json(self) -> str:
        return json.dumps(self.dict())

class TestBase(unittest.TestCase):
    """
    Base class for tests that need to instantiate a ChatBot, but not necessarily run inference with it.
    Use `TestBaseRunner`, a derived class of this class, for those tests.
    """
    default_confidence_threshold = ChatBot.default_confidence_threshold
    default_rating_threshold = 4
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
            response_handler = ChatBotResponseHandler(
                confidence_level_threshold = self.confidence_threshold, 
                logger = logger),
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
        self.model                         = os.environ.get('MODEL', 'ollama_chat/gpt-oss:20b')
        self.service_url                   = os.environ.get('INFERENCE_URL', 'http://localhost:11434')
        self.template_dir                  = os.environ.get('PROMPTS_TEMPLATES_DIR', 'prompts/templates')
        self.data_dir                      = os.environ.get('DATA_DIR', 'data')
        self.accumulate_test_results: bool = bool(os.environ.get('ACCUMULATE_TEST_ERRORS', False))
        self.sample_rate: float            = float(os.environ.get('DATA_SAMPLE_RATE', 1.0))
        self.rating_threshold: int         = int(os.environ.get('RATING_THRESHOLD', TestBase.default_rating_threshold))
        self.confidence_threshold: float   = float(os.environ.get('CONFIDENCE_THRESHOLD', TestBase.default_confidence_threshold))
        self.verbose: bool                 = bool(os.environ.get('VERBOSE', False))

        self.samples_count: int = 0
        self.key_results = {'low_confidence_results': [], 'errors': [], 'warnings': []}

        self.make_chatbot()

class TestBaseRunner(TestBase):
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
    * Accumulating all errors and warnings vs. failing fast:
        We have found it useful to accumulate and report all found errors and warnings 
        vs. the normal approach of failing fast on the first error.
    """

    total_lcr_count = 0
    total_error_count = 0
    total_warning_count = 0
    benchmark_data_dir = Path("tests/data")

    def setUp(self):
        super().setUp()
        
        d = {
            'step' :                        'setUp',
            'model':                        self.model,
            'service_url':                  self.service_url,
            'template_dir':                 self.template_dir,
            'data_dir':                     self.data_dir,
            'accumulate_test_results':      self.accumulate_test_results,
            'default sample_rate':          self.sample_rate,
            'default rating_threshold':     self.rating_threshold,
            'default confidence_threshold': self.confidence_threshold,
        }
        print(json.dumps(d), file=TestBaseRunner.log_file)

    def tearDown(self):
        lcr_count      = len(self.key_results['low_confidence_results'])
        warning_count  = len(self.key_results['warnings'])
        error_count    = len(self.key_results['errors'])

        TestBaseRunner.total_lcr_count     += lcr_count
        TestBaseRunner.total_warning_count += warning_count
        TestBaseRunner.total_error_count   += error_count
        self._dump_key_results(lcr_count, warning_count, error_count)

    def _dump_key_results(self, lcr_count: int, warning_count: int, error_count: int):
        lcrs = [lcr.dict() for lcr in self.key_results['low_confidence_results']]
        d = {
            'step':              'tearDown',
            'samples_count':     self.samples_count,
            'low_confidence_results': {
                'count':         lcr_count,
                'results':       lcrs,
            },
            'warnings': {
                'count':         warning_count,
                'warnings':      self.key_results['warnings'],
            },
            'errors': {
                'count':         error_count,
                'errors':        self.key_results['errors'],
            },
        }
        js1 = json.dumps(d)
        js  = re.sub(r'\n', r'\\n', js1)  # Try to print true JSONL records
        print(js, file=TestBaseRunner.log_file)
        if not self.samples_count:
            raise ValueError(f"No samples were loaded!")            

    @classmethod
    def setUpClass(cls):
        def_log_dir = "tests/logs"
        log_file_template = os.environ.get('TESTS_LOGS_FILE_TEMPLATE')
        if not log_file_template:
            print("WARNING: TESTS_LOGS_FILE_TEMPLATE undefined. Using default value.")
            log_file_template = f"{def_log_dir}/{{class_name}}-{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"

        log_file_path = Path(log_file_template.format(class_name=cls.__name__))
        print(f"\n  ** Logging to {log_file_path} ** \n")
        os.makedirs(log_file_path.parent, exist_ok=True)
        TestBaseRunner.log_file = log_file_path.open('a') # append mode, because we _may_ share it across tests.

    @classmethod
    def tearDownClass(cls):
        print(f"\nTotals:")
        print(f"Low-confidence results: {TestBaseRunner.total_lcr_count}")
        print(f"Warning count:          {TestBaseRunner.total_warning_count}")
        print(f"Error count:            {TestBaseRunner.total_error_count}")
        print()
        if TestBaseRunner.log_file:
            TestBaseRunner.log_file.close()
        if TestBaseRunner.total_error_count:
            raise AssertionError(f"{TestBaseRunner.total_error_count} errors reported!")

    def load_test_data(self, path: Path) -> list[TestPrompt]:
        if not path.exists():
            raise FileNotFoundError(path)

        prompts = []
        with path.open('r') as file:
            for line in file:
                ls = line.strip()
                if ls:
                    try:
                        obj     = parse_json(ls)
                        query   = dict_pop(obj, 'query')
                        labels  = dict_pop(obj, 'labels')
                        actions = dict_pop(obj, 'actions')
                        rating  = dict_pop(obj, 'rating')
                        reason  = dict_pop(obj, 'reason') # Not all records have this, so None will be returned.
                        # What's left in obj at this point are "substitution" keywords, if any,
                        # that we expect to find in the inference results.
                        tp = TestPrompt(query, labels, actions, rating, reason, keywords=obj)
                        prompts.append(tp)
                    except ValueError as err:
                        raise ValueError(f"From file <{file}>, error parsing line: <{line}>") from err
        if not len(prompts):
            raise ValueError(f"No prompts were loaded from {file}!")
        return prompts

    def try_query(self, 
        test_prompt: TestPrompt,
        rating_threshold: int = TestBase.default_rating_threshold,
        confidence_threshold: float = TestBase.default_confidence_threshold):
        """
        See src/apps/prompts/templates/patient-chatbot.yaml for "requirements".
        Rather than follow the usual approach for failing fast on the first wrong datum, 
        we run all the examples and accumulate error messages, then report the results.
        Compare to `try_query()`.
        """
        exp_query    = test_prompt.query
        exp_labels   = test_prompt.labels
        exp_actions  = test_prompt.actions
        exp_rating   = test_prompt.rating
        exp_keywords = test_prompt.keywords
        prompt       = exp_query # no longer used: if not exp_keywords else exp_query.format_map(exp_keywords)
        
        metadata = {
            'prompt': prompt,
            'test_prompt': test_prompt.dict(),
            'rating_threshold': rating_threshold,
            'confidence_threshold': confidence_threshold,
        }
        # On success this will be returned as empty. If problems are found,
        # we put those kvs first, so they are printed first...
        errors = {}
        warnings = {}

        answer = self.chatbot.query(prompt)
        if isinstance(answer, str):
            qf = {
                'query_failure': f"Error message returned: {answer}",
                'metadata':      metadata,
            }
            self.key_results['errors'].append(qf)
            if self.verbose:
                print(qf)
            return qf
        else:
            metadata['answer'] = answer

        actual_query1        = str(answer.get('query'))
        actual_rtu           = answer.get('reply_to_user')
        actual_content       = answer.get('content', {})
        actual_query2        = str(actual_content.get('query'))
        actual_reply         = actual_content.get('reply')
        actual_label         = actual_reply.get('label')
        actual_actions       = re.split(r'\s*,\s*', actual_reply.get('actions', ''))
        actual_keywords      = dict([(key, actual_reply.get(key, '')) for key in exp_keywords])
        # We have seen the occasional confidence scores at the content level, rather than inside the reply.
        actual_confidence    = actual_reply.get('confidence', actual_content.get('confidence', 1.0))
        # actual_text          = actual_reply.get('text', '')

        # We have seen subtle punctuation changes in prompts...
        p2  = re.sub(r'\W', ' ', prompt)
        aq1 = re.sub(r'\W', ' ', actual_query1)
        aq2 = re.sub(r'\W', ' ', actual_query2)
        if p2 != aq1:
            errors['unexpected answer.query'] = f"{prompt} != {actual_query1}"
        if p2 != aq2:
            errors['unexpected content.query'] = f"{prompt} != {actual_query2}"
        
        low_confidence_reasons = []
        if actual_confidence < confidence_threshold:
            low_confidence_reasons.append(f"Actual confidence ({actual_confidence}) < confidence threshold ({confidence_threshold}).")
        if exp_rating < rating_threshold:
            low_confidence_reasons.append(f"Expected rating ({exp_rating}) < rating threshold ({rating_threshold}).")

        if low_confidence_reasons:
            reasons = ' '.join(low_confidence_reasons)
            lcr = LowConfidenceResult(prompt, reasons, actual_reply, test_prompt, rating_threshold, confidence_threshold)
            self.key_results['low_confidence_results'].append(lcr)
            if self.verbose:
                print(lcr)
        else:
            err_msg = self._check_label(exp_labels, actual_label)
            if len(err_msg) > 0:
                errors['unexpected label'] = err_msg
            elif actual_label == 'emergency' or actual_label == 'other':
                # Ignore the action if we detect an emergency or other prompt, but check
                # the returned user response, since we always return with the same reply for 
                # these labels!
                exp_rtu = ChatBotResponseHandler.replies[actual_label]
                if exp_rtu != actual_rtu:
                    errors['unexpected reply_to_user'] = f"<{exp_rtu}> != <{actual_rtu}>"
            else:
                # For the other label cases, IF there are expected actions, do the actual actions contain
                # at least one item in the expected actions? This is not a rigorous requirement, but should
                # be adequate. The ChatBot can return more than one actions in a comma-separated list, so 
                # we check at least one of the actual actions is in the set of the expected actions. This
                # is done by computing the intersection of the sets and expecting it to be non-empty.
                # Right now, we treat these as warnings, not errors.
                if exp_actions:
                    exp_set = set(exp_actions)
                    actual_set = set(actual_actions)
                    if not len(actual_set.intersection(exp_set)):
                        warnings['unexpected actions'] = f"""At least one actual action {actual_actions} not found in the allowed (expected) actions = {exp_actions}."""

            # For the "keywords", ignore case, since sometimes proper names,
            # can occur with different cases. Also, we check that _expected_
            # values, if any, are present, but also allow for additional actual
            # values. This is because some of the test queries hard-code potential
            # keywords, but we don't "care" if they appear.
            # Right now, we treat these as warnings, not errors.
            missing_kvs = {}
            for key, value in exp_keywords.items():
                if len(value) == 0:
                    warnings['unexpected keywords'] = f"BUG: keyword {key} has zero-length value array!"
                    continue
                if len(value) > 1:
                    warnings['unexpected keywords'] = f"TODO: We currently only handle one value in keywords: {key} -> {value}. Ignoring all but the first value!"
                expected = value[0].lower()
                actual   = actual_keywords.get(key, '').lower()
                if not actual.find(expected) >= 0:
                    missing_kvs[key] = f"{expected} vs. {actual}"
            if missing_kvs:
                warnings['unexpected keywords'] = missing_kvs

        if errors:
            me = errors | metadata
            self.key_results['errors'].append(me)
            if self.verbose:
                print(me)
        if warnings:
            mw = warnings | metadata
            self.key_results['warnings'].append(mw)
            if self.verbose:
                print(mw)

    def try_queries(self, 
        file_name: Path | str, 
        sample_rate: float = 0.0, 
        rating_threshold: int = TestBase.default_rating_threshold,
        confidence_threshold: float = TestBase.default_confidence_threshold):
        """
        Loop through the sampled test queries and try them.
        If the environment variable `ACCUMULATE_TEST_ERRORS` is true (any value non-empty),
        then accumulate errors and report them at the end. Otherwise, fail on the first prompt
        where we detect errors in the result.
        """ 
        if not sample_rate > 0.0:
            sample_rate = self.sample_rate

        d = {
            'step':                    'try_queries',
            'file_name':               str(file_name),
            'sample_rate':             sample_rate,
            'rating_threshold':        rating_threshold,
            'confidence_threshold':    confidence_threshold,
            'accumulate_test_results': self.accumulate_test_results,
        }
        print(json.dumps(d), file=TestBaseRunner.log_file)

        test_prompts = self.load_test_data(Path(file_name))
        samples = self._sample(test_prompts, sample_rate) if sample_rate < 1.0 else test_prompts
        self.samples_count += len(samples)

        last_time = time.time()
        slow_count = 0
        allowed_time_delta = 120 # seconds (NOTE: litellm appears to have an internal timeout of 5-6 minutes.)

        for test_prompt in samples:
            self.try_query(test_prompt,
                rating_threshold=rating_threshold,
                confidence_threshold=confidence_threshold)
            
            lcr_count      = len(self.key_results['low_confidence_results'])
            warning_count  = len(self.key_results['warnings'])
            error_count    = len(self.key_results['errors'])
            if not self.accumulate_test_results:
                self.assertTrue(error_count == 0, f"{error_count} errors for test prompt: {test_prompt}")

            # Logic to detect when it appears the system has deadlocked in some way.
            # If so, then error out.
            now = time.time()
            difference = int(last_time - now)
            self.assertLess(difference, allowed_time_delta, f"Time difference between inference calls, {difference} exceeds allowed time delta {allowed_time_delta}")
            last_time = now

            # Show we aren't dead by printing counts...
            print(f"({lcr_count},{warning_count},{error_count}),", end='')  

    def _sample(self, collection: list[Any], sample_rate: float) -> list[Any]:
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

    def _check_label(self, expected: list[str], actual: str) -> str:
        return "" if actual in expected else f"""label '{actual}' not in expected: {expected}."""
