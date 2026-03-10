"""Langflow component for UnitBenchmarkDataSynthesizer."""
import logging
from typing import Optional
from langflow.custom import Component
from langflow.io import MessageTextInput, Output, IntInput, StrInput
from langflow.schema import Data

import sys
from pathlib import Path

# Add parent directory to path to import from tools
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.unit_benchmark import UnitBenchmarkDataSynthesizer


class UnitBenchmarkDataSynthesizerComponent(Component):
    """Langflow component wrapper for UnitBenchmarkDataSynthesizer."""
    
    display_name = "Benchmark Data Synthesizer"
    description = "Synthesizes Q&A benchmark data for healthcare chatbot testing"
    icon = "database"
    
    inputs = [
        StrInput(
            name="model_name",
            display_name="Model Name",
            info="The LLM model to use for synthesis",
            value="ollama_chat/gpt-oss:20b",
        ),
        StrInput(
            name="service_url",
            display_name="Service URL",
            info="The inference service URL",
            value="http://localhost:11434",
        ),
        StrInput(
            name="template_dir",
            display_name="Template Directory",
            info="Directory containing prompt templates",
            value="prompts/templates",
        ),
        StrInput(
            name="data_dir",
            display_name="Data Directory",
            info="Directory where synthetic data will be written",
            value="data",
        ),
        StrInput(
            name="use_case",
            display_name="Use Case",
            info="Specific use case to generate (leave empty for all)",
            value="",
        ),
    ]
    
    outputs = [
        Output(display_name="Results", name="results", method="synthesize_data"),
    ]
    
    def synthesize_data(self) -> Data:
        """Execute the data synthesis."""
        # Setup logger
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.INFO)
        
        # Create synthesizer instance
        synthesizer = UnitBenchmarkDataSynthesizer(
            model_name=self.model_name,
            service_url=self.service_url,
            template_dir=self.template_dir,
            data_dir=self.data_dir,
            logger=logger
        )
        
        # Generate data
        if self.use_case:
            # Generate for specific use case
            from common.utils import use_cases
            cases = use_cases()
            if self.use_case in cases:
                label = cases[self.use_case]
                substr = self.use_case.replace(' ', '-')
                num_unexpected = synthesizer.generate(substr, label)
                result_msg = f"Generated data for '{self.use_case}' with {num_unexpected} unexpected labels"
            else:
                result_msg = f"Unknown use case: {self.use_case}"
        else:
            # Generate all
            synthesizer.generate_all()
            result_msg = "Generated data for all use cases"
        
        self.status = result_msg
        
        return Data(
            data={
                "status": "success",
                "message": result_msg,
                "model": self.model_name,
                "data_dir": self.data_dir,
            }
        )

# Made with Bob
