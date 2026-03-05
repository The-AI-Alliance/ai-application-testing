# Common code for tests of the "ChatBot" module using Hypothesis for property-based testing.
# https://hypothesis.readthedocs.io/en/latest/

from hypothesis import given, strategies as st
import json, os, random, re, sys, unittest
from json.decoder import JSONDecodeError
from pathlib import Path
from io import StringIO

from apps.chatbot import ChatBot, ChatBotShell

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

    place_holders = {
        'prescriptions': ['prilosec', 'xanax'],
        'body_parts': ['stomach', 'heart'],
    }

    def make_chatbot(self) -> (ChatBot, ChatBotShell):
        model = os.environ.get('MODEL', 'ollama_chat/gpt-oss:20b')
        service_url = os.environ.get('INFERENCE_URL', 'http://localhost:11434')
        template_dir = os.environ.get('PROMPTS_TEMPLATES_DIR', 'prompts/templates')
        data_dir = os.environ.get('DATA_DIR', '../output/ollama_chat/gpt-oss_20b/data')
        if bool(os.environ.get('VERBOSE', False)):
            print(f"model:        {model}")
            print(f"service_url:  {service_url}")
            print(f"template_dir: {template_dir}")
            print(f"data_dir:     {data_dir}")
    
        chatbot = ChatBot(
            model = model,
            service_url = service_url,
            template_dir = template_dir,
            data_dir = data_dir)
        shell = ChatBotShell(chatbot, stdout = StringIO())
        return chatbot, shell

    def parse_json(self, text: any) -> dict[str,any]:
        try:
            obj = json.loads(text)
            return obj
        except (JSONDecodeError, TypeError) as err:
            print(f"ERROR {err}: text not JSON? <{text}> (type: {type(text)})")
            raise Exception from err

    def setUp(self):
        """
        Initialize the ChatBot and ChatBotShell. Track the number of confident and "low-confidence" results.
        By default, all test data prompts are executed, which can be too slow and expensive for frequent 
        unit tests. Override the environment variable `DATA_SAMPLE_RATE` when invoking tests with a value
        between 0.0 (none) and 1.0 (all) to control the amount of test data prompts sampled. (A minimum 
        threshold of 5 samples, if available, will be used in all cases.)
        """
        chatbot, shell = self.make_chatbot()
        self.chatbot = chatbot
        self.shell = shell
        self.low_confidence_results: [LowConfidenceResult] = []
        self.samples_count: int = 0
        self.def_sample_rate: float = float(os.environ.get('DATA_SAMPLE_RATE', 1.0))
        print(f"Using default sampling rate: {self.def_sample_rate}")

    def tearDown(self):
        if self.low_confidence_results:
            ratio = f"{len(self.low_confidence_results)}/{self.samples_count}"
            print(f"{__file__}: Minimal checking was done on the following {ratio} 'low-confidence results':")
            for lcr in self.low_confidence_results:
                print(lcr)
            print()
        
    def load_test_data(self, path: Path) -> [TestPrompt]:
        if not path.exists():
            raise FileNotFoundError(path)

        prompts = []
        with path.open('r') as file:
            for line in file:
                obj     = self.parse_json(line)
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
        rating_threshold: int = 4,
        confidence_threshold: float = 0.6):
        """See src/apps/prompts/templates/patient-chatbot.yaml for "requirements"."""
        query   = test_prompt.query
        label   = test_prompt.label
        actions = test_prompt.actions
        rating  = test_prompt.rating
        exp_place_holders = {}
        for key, value in place_holders.items():
            exp_place_holders[key] = value if query.find('{'+key+'}') >= 0 else ''
        prompt = query.format_map(place_holders)
        answer = self.chatbot.query(prompt)
        query1 = answer.get('query')
        response_json = answer.get('response')
        response = self.parse_json(response_json)
        query2 = response.get('query')
        reply  = response.get('reply')
        confidence = reply.get('confidence')
        err_msg = f"prompt: {prompt}, response: {response}, test_prompt: {test_prompt}"
        self.assertEqual(prompt, query1, err_msg)
        self.assertEqual(prompt, query2, err_msg)
        if confidence >= confidence_threshold and rating >= rating_threshold:
            self.assertEqual(label,   reply['label'],   err_msg)
            self.assertEqual(actions, reply['actions'], err_msg)
            # For the "place holders", ignore case. This is because sometimes proper names,
            # like for pharmaceuticals can occur with different cases.
            for key in place_holders:
                expected = exp_place_holders.get(key).lower()
                actual   = reply.get(key).lower()
                self.assertEqual(expected, actual, f"for key = {key}: {err_msg}")
        else:
            self.low_confidence_results.append(LowConfidenceResult(reply, test_prompt, rating_threshold, confidence_threshold))
    
    def _sample(self, collection: list[any], sample_rate: float) -> list[any]:
        """
        The sample_rate (between 0.0 and 1.0) is a pragmatic compromise due to relatively slow local inference
        and expensive inference services. Use a low value for unit tests that are run frequently and need to be fast.
        Use a high value for integration and acceptance tests, usually 1.0, to run most or all of the available test
        prompts, for more exhaustive coverage. However, if the total number of test prompts is less than 5 (arbitrary),
        we run all of them, for any sample_rate > 0.
        """
        if not sample_rate:
            sample_rate = self.def_sample_rate        
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

    def try_queries(self, file_name: str, place_holders: dict[str,str], sample_rate: float = None, rating_threshold: int = 4, confidence_threshold: float = 0.6):
        test_prompts = self.load_test_data(Path(file_name))
        samples = self._sample(test_prompts, sample_rate)
        self.samples_count = len(samples)
        for test_prompt in samples:
            self.try_query(test_prompt, place_holders, rating_threshold=rating_threshold, confidence_threshold=confidence_threshold)
