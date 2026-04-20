"""Langflow component for UnitBenchmarkDataSynthesizer."""
import logging
from typing import Optional
from lfx.custom.custom_component.component import Component
from lfx.io import MessageTextInput, IntInput, Output, MultiselectInput, StrInput
from lfx.schema.data import Data

import sys
from pathlib import Path

# Add parent directory to path to import from tools
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.langflow.unit_benchmark_flow import UnitBenchmarkFlowOrchestrator


class UnitBenchmarkDataSynthesizerComponent(Component):
    """Langflow component wrapper for UnitBenchmarkFlowOrchestrator."""
    
    display_name = "Unit Benchmark Data Synthesis"
    description = "Synthesize and validate Q&A benchmark data for testing a healthcare ChatBot."
    name = "UnitBenchmarkDataSynthesizerValidator"
    icon = "code"
    
    inputs = [
        StrInput(
            name="model_name",
            display_name="Model Name",
            info="The LLM model to use for synthesis",
            value="ollama_chat/gemma4:e4b",
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
            value="tools/prompts/templates",
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
        # TODO: This is tricky to support correctly, so we will leave this hear and
        # add support in a future release.
        # MultiselectInput(
        #     name="processing_steps",
        #     display_name="Which processing steps?",
        #     info="Which processing steps should be performed?",
        #     value=["Data synthesis", "Data validation", "Validation statistics"],
        # )
    ]
    
    outputs = [
        Output(display_name="Results", name="results", method="synthesize_data"),
    ]
    
    def synthesize_data(self) -> Data:
        """Execute the data synthesis."""
        # Setup logger
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.INFO)
        
        # Create the orchestrator instance.

        orchestrator = UnitBenchmarkFlowOrchestrator(
            model_name=self.model_name,
            service_url=self.service_url,
            template_dir=self.template_dir,
            data_dir=self.data_dir,
            use_case=self.use_case,
            just_synthesis=False,
            just_validation=False,
            just_stats=False,
            logger=logger
        )

        # Run the pipeline
        results = orchestrator.run_full_pipeline()
        
        logger.info(f"Pipeline completed with status: {results['status']}")
        
        if results.get('status') == 'success':
            logger.info("Pipeline execution successful!")
        else:
            logger.error(f"Pipeline failed: {results.get('message', 'Unknown error')}")
            sys.exit(1)    
        
        return Data(
            data={
                "status": results.get('status', "'status' unknown!"),
                "message": results.get('message', "'message' unknown!"),
                "synthesis_results": results.get('synthesis_results', "No synthesis results available!"),
                "validation_results": results.get('validation_results', "No validation results available!"),
            }
        )

