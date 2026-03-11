"""Unit tests for the benchmark flow orchestrator."""
import unittest
import json
import logging
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tools.langflow.unit_benchmark_flow import UnitBenchmarkFlowOrchestrator

# TODO: Move this to an integration test and replace the mocks with real calls to Langflow.

class TestUnitBenchmarkFlowOrchestrator(unittest.TestCase):
    """Test cases for UnitBenchmarkFlowOrchestrator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.model_name = "test_model"
        self.service_url = "http://test:1234"
        self.template_dir = os.path.join(self.temp_dir, "templates")
        self.data_dir = os.path.join(self.temp_dir, "data")
        
        # Create directories
        os.makedirs(self.template_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Create a test logger
        self.logger = logging.getLogger("test")
        self.logger.setLevel(logging.DEBUG)
        
        self.orchestrator = UnitBenchmarkFlowOrchestrator(
            model_name=self.model_name,
            service_url=self.service_url,
            template_dir=self.template_dir,
            data_dir=self.data_dir,
            use_case='',
            just_synthesis=True,
            just_validation=True,
            just_stats=True,
            logger=self.logger
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test orchestrator initialization."""
        self.assertEqual(self.orchestrator.model_name, self.model_name)
        self.assertEqual(self.orchestrator.service_url, self.service_url)
        self.assertEqual(self.orchestrator.template_dir, self.template_dir)
        self.assertEqual(self.orchestrator.data_dir, self.data_dir)
        self.assertIsNone(self.orchestrator.synthesis_results)
        self.assertIsNone(self.orchestrator.validation_results)
    
    # TODO eliminate the mocks and make real test doubles.
    # @patch('tools.langflow.unit_benchmark_flow.BenchMarkDataSynthesizer')
    # def test_run_synthesis_all_cases(self, mock_synthesizer_class):
    #     """Test running synthesis for all use cases."""
    #     # Setup mock
    #     mock_synthesizer = Mock()
    #     mock_synthesizer_class.return_value = mock_synthesizer
        
    #     # Run synthesis
    #     result = self.orchestrator.run_synthesis()
        
    #     # Verify
    #     mock_synthesizer_class.assert_called_once_with(
    #         model_name=self.model_name,
    #         service_url=self.service_url,
    #         template_dir=self.template_dir,
    #         data_dir=self.data_dir,
    #         logger=self.logger
    #     )
    #     mock_synthesizer.generate_data.assert_called_once()
        
    #     self.assertEqual(result['status'], 'success')
    #     self.assertEqual(result['use_case'], 'all')
    #     self.assertEqual(result['data_dir'], self.data_dir)
    
    # @patch('tools.langflow.unit_benchmark_flow.BenchMarkDataSynthesizer')
    # def test_run_synthesis_specific_case(self, mock_synthesizer_class):
    #     """Test running synthesis for a specific use case."""
    #     # Setup mock
    #     mock_synthesizer = Mock()
    #     mock_synthesizer.generate_data_for_use_case.return_value = 0
    #     mock_synthesizer_class.return_value = mock_synthesizer
        
    #     # Run synthesis for specific case
    #     use_case = "prescription refills"
    #     result = self.orchestrator.run_synthesis(use_case=use_case)
        
    #     # Verify
    #     mock_synthesizer.generate_data_for_use_case.assert_called_once()
    #     self.assertEqual(result['status'], 'success')
    #     self.assertEqual(result['use_case'], use_case)
    #     self.assertEqual(result['unexpected_labels'], 0)
    
    # @patch('tools.langflow.unit_benchmark_flow.BenchMarkDataSynthesizer')
    # def test_run_synthesis_unknown_case(self, mock_synthesizer_class):
    #     """Test running synthesis with unknown use case."""
    #     # Setup mock
    #     mock_synthesizer = Mock()
    #     mock_synthesizer_class.return_value = mock_synthesizer
        
    #     # Run synthesis with unknown case
    #     result = self.orchestrator.run_synthesis(use_case="unknown_case")
        
    #     # Verify
    #     self.assertEqual(result['status'], 'error')
    #     self.assertIn('Unknown use case', result['message'])
    
    # @patch('tools.langflow.unit_benchmark_flow.BenchMarkDataValidator')
    # def test_run_validation(self, mock_validator_class):
    #     """Test running validation."""
    #     # Setup mock
    #     mock_validator = Mock()
    #     mock_stats = {
    #         'file1.json': {
    #             'data-file': 'file1.json',
    #             'validation-file': 'file1-validation.json',
    #             'ratings': [1, 2, 3, 4, 5],
    #             'total_count': 15,
    #             'error_count': 0
    #         }
    #     }
    #     mock_validator.validate.return_value = mock_stats
    #     mock_validator_class.return_value = mock_validator
        
    #     # Run validation
    #     result = self.orchestrator.run_validation(just_stats=False)
        
    #     # Verify
    #     mock_validator_class.assert_called_once_with(
    #         just_stats=False,
    #         model_name=self.model_name,
    #         service_url=self.service_url,
    #         template_dir=self.template_dir,
    #         data_dir=self.data_dir,
    #         logger=self.logger
    #     )
    #     mock_validator.validate.assert_called_once()
    #     mock_validator.print_stats.assert_called_once_with(mock_stats)
        
    #     self.assertEqual(result['status'], 'success')
    #     self.assertEqual(result['stats'], mock_stats)
    
    # @patch('tools.langflow.unit_benchmark_flow.BenchMarkDataValidator')
    # @patch('tools.langflow.unit_benchmark_flow.BenchMarkDataSynthesizer')
    # def test_run_full_pipeline_success(self, mock_synthesizer_class, mock_validator_class):
    #     """Test running the full pipeline successfully."""
    #     # Setup mocks
    #     mock_synthesizer = Mock()
    #     mock_synthesizer_class.return_value = mock_synthesizer
        
    #     mock_validator = Mock()
    #     mock_stats = {'file1.json': {'ratings': [1, 2, 3, 4, 5]}}
    #     mock_validator.validate.return_value = mock_stats
    #     mock_validator_class.return_value = mock_validator
        
    #     # Run full pipeline
    #     result = self.orchestrator.run_full_pipeline()
        
    #     # Verify
    #     self.assertEqual(result['status'], 'success')
    #     self.assertIn('synthesis_results', result)
    #     self.assertIn('validation_results', result)
    #     self.assertEqual(result['synthesis_results']['status'], 'success')
    #     self.assertEqual(result['validation_results']['status'], 'success')
    
    # @patch('tools.langflow.unit_benchmark_flow.BenchMarkDataSynthesizer')
    # def test_run_full_pipeline_synthesis_failure(self, mock_synthesizer_class):
    #     """Test full pipeline when synthesis fails."""
    #     # Setup mock to simulate failure
    #     mock_synthesizer = Mock()
    #     mock_synthesizer_class.return_value = mock_synthesizer
        
    #     # Patch run_synthesis to return error
    #     with patch.object(self.orchestrator, 'run_synthesis') as mock_run_synthesis:
    #         mock_run_synthesis.return_value = {
    #             'status': 'error',
    #             'message': 'Synthesis failed'
    #         }
            
    #         # Run full pipeline
    #         result = self.orchestrator.run_full_pipeline()
            
    #         # Verify
    #         self.assertEqual(result['status'], 'error')
    #         self.assertIn('Synthesis failed', result['message'])


if __name__ == '__main__':
    unittest.main()

