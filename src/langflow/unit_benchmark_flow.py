"""
Langflow flow orchestrator for benchmark data synthesis and validation.

This module provides a programmatic interface to run the benchmark data
synthesis and validation pipeline without requiring Langflow to be installed.
It can also generate a Langflow-compatible JSON flow definition.
"""
import os
import sys
import json
import logging
import importlib.util
from pathlib import Path
from typing import Dict, Any, Optional

from common.utils import setup
from tools.unit_benchmark import UnitBenchmarkDataSynthesizer, UnitBenchmarkDataValidator

class UnitBenchmarkFlowOrchestrator:
    """Orchestrates the benchmark data synthesis and validation pipeline."""
    
    def __init__(
        self,
        model_name: str,
        service_url: str,
        template_dir: str,
        data_dir: str,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the flow orchestrator.
        
        Args:
            model_name: The LLM model to use
            service_url: The inference service URL
            template_dir: Directory containing prompt templates
            data_dir: Directory for data files
            logger: Optional logger instance
        """
        self.model_name = model_name
        self.service_url = service_url
        self.template_dir = template_dir
        self.data_dir = data_dir
        self.logger = logger or logging.getLogger(__name__)
        
        self.synthesis_results = None
        self.validation_results = None
    
    def run_synthesis(self, use_case: Optional[str] = None) -> Dict[str, Any]:
        """
        Run the data synthesis step.
        
        Args:
            use_case: Optional specific use case to generate. If None, generates all.
            
        Returns:
            Dictionary with synthesis results
        """
        self.logger.info("Starting benchmark data synthesis...")
        
        synthesizer = UnitBenchmarkDataSynthesizer(
            model_name=self.model_name,
            service_url=self.service_url,
            template_dir=self.template_dir,
            data_dir=self.data_dir,
            logger=self.logger
        )
        
        if use_case:
            from common.utils import use_cases
            cases = use_cases()
            if use_case in cases:
                label = cases[use_case]
                substr = use_case.replace(' ', '-')
                num_unexpected = synthesizer.generate(substr, label)
                self.synthesis_results = {
                    "status": "success",
                    "use_case": use_case,
                    "unexpected_labels": num_unexpected,
                    "data_dir": self.data_dir
                }
            else:
                self.synthesis_results = {
                    "status": "error",
                    "message": f"Unknown use case: {use_case}"
                }
        else:
            synthesizer.generate_all()
            self.synthesis_results = {
                "status": "success",
                "use_case": "all",
                "data_dir": self.data_dir
            }
        
        self.logger.info(f"Synthesis completed: {self.synthesis_results}")
        return self.synthesis_results
    
    def run_validation(self, just_stats: bool = False) -> Dict[str, Any]:
        """
        Run the data validation step.
        
        Args:
            just_stats: If True, only compute statistics without re-validating
            
        Returns:
            Dictionary with validation results
        """
        self.logger.info("Starting benchmark data validation...")
        
        validator = UnitBenchmarkDataValidator(
            just_stats=just_stats,
            model_name=self.model_name,
            service_url=self.service_url,
            template_dir=self.template_dir,
            data_dir=self.data_dir,
            logger=self.logger
        )
        
        total_stats = validator.validate()
        validator.print_stats(total_stats)
        
        self.validation_results = {
            "status": "success",
            "stats": total_stats,
            "data_dir": self.data_dir
        }
        
        self.logger.info("Validation completed")
        return self.validation_results
    
    def run_full_pipeline(
        self,
        use_case: Optional[str] = None,
        just_stats: bool = False
    ) -> Dict[str, Any]:
        """
        Run the complete pipeline: synthesis followed by validation.
        
        Args:
            use_case: Optional specific use case to generate
            just_stats: If True, only compute validation statistics
            
        Returns:
            Dictionary with complete pipeline results
        """
        self.logger.info("Starting full benchmark pipeline...")
        
        # Step 1: Synthesis
        synthesis_results = self.run_synthesis(use_case)
        
        if synthesis_results.get("status") != "success":
            return {
                "status": "error",
                "message": "Synthesis failed",
                "synthesis_results": synthesis_results
            }
        
        # Step 2: Validation
        validation_results = self.run_validation(just_stats)
        
        return {
            "status": "success",
            "synthesis_results": synthesis_results,
            "validation_results": validation_results
        }
    
    def export_langflow_json(self, output_file: str) -> None:
        """
        Export a Langflow-compatible JSON flow definition.
        
        Args:
            output_file: Path to write the JSON flow definition
        """
        flow_definition = {
            "name": "Benchmark Data Pipeline",
            "description": "Synthesizes and validates benchmark Q&A data for healthcare chatbot",
            "nodes": [
                {
                    "id": "synthesizer",
                    "type": "CustomComponent",
                    "data": {
                        "type": "UnitBenchmarkDataSynthesizer",
                        "node": {
                            "template": {
                                "model_name": {
                                    "value": self.model_name,
                                    "type": "str"
                                },
                                "service_url": {
                                    "value": self.service_url,
                                    "type": "str"
                                },
                                "template_dir": {
                                    "value": self.template_dir,
                                    "type": "str"
                                },
                                "data_dir": {
                                    "value": self.data_dir,
                                    "type": "str"
                                }
                            },
                            "description": "Synthesizes Q&A benchmark data"
                        }
                    },
                    "position": {"x": 100, "y": 100}
                },
                {
                    "id": "validator",
                    "type": "CustomComponent",
                    "data": {
                        "type": "UnitBenchmarkDataValidator",
                        "node": {
                            "template": {
                                "model_name": {
                                    "value": self.model_name,
                                    "type": "str"
                                },
                                "service_url": {
                                    "value": self.service_url,
                                    "type": "str"
                                },
                                "template_dir": {
                                    "value": self.template_dir,
                                    "type": "str"
                                },
                                "data_dir": {
                                    "value": self.data_dir,
                                    "type": "str"
                                },
                                "just_stats": {
                                    "value": False,
                                    "type": "bool"
                                }
                            },
                            "description": "Validates synthesized benchmark data"
                        }
                    },
                    "position": {"x": 400, "y": 100}
                }
            ],
            "edges": [
                {
                    "id": "synthesizer-validator",
                    "source": "synthesizer",
                    "target": "validator",
                    "sourceHandle": "output",
                    "targetHandle": "input"
                }
            ]
        }
        
        with open(output_file, 'w') as f:
            json.dump(flow_definition, f, indent=2)
        
        self.logger.info(f"Langflow JSON definition exported to {output_file}")


def main():
    """Main entry point for running the benchmark flow."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run benchmark data synthesis and validation pipeline"
    )
    parser.add_argument(
        "-m", "--model",
        default="ollama_chat/gpt-oss:20b",
        help="Model name to use"
    )
    parser.add_argument(
        "-s", "--service-url",
        default="http://localhost:11434",
        help="Inference service URL"
    )
    parser.add_argument(
        "-t", "--template-dir",
        default="prompts/templates",
        help="Template directory"
    )
    parser.add_argument(
        "-d", "--data-dir",
        default="data",
        help="Data directory"
    )
    parser.add_argument(
        "-u", "--use-case",
        default=None,
        help="Specific use case to generate (default: all)"
    )
    parser.add_argument(
        "-j", "--just-stats",
        action="store_true",
        help="Only compute validation statistics"
    )
    parser.add_argument(
        "--export-json",
        help="Export Langflow JSON definition to specified file"
    )
    parser.add_argument(
        "-l", "--log-file",
        default="logs/benchmark-flow.log",
        help="Log file path"
    )
    parser.add_argument(
        "--log-level",
        type=int,
        default=logging.INFO,
        help="Logging level"
    )
    
    args = parser.parse_args()
    
    # Setup logger
    from common.utils import make_logger
    logger = make_logger(args.log_file, name="benchmark-flow", level=args.log_level)
    
    # Create orchestrator
    orchestrator = UnitBenchmarkFlowOrchestrator(
        model_name=args.model,
        service_url=args.service_url,
        template_dir=args.template_dir,
        data_dir=args.data_dir,
        logger=logger
    )
    
    # Export JSON if requested
    if args.export_json:
        orchestrator.export_langflow_json(args.export_json)
        logger.info(f"Langflow JSON exported to {args.export_json}")
        return
    
    # Run the pipeline
    results = orchestrator.run_full_pipeline(
        use_case=args.use_case,
        just_stats=args.just_stats
    )
    
    logger.info(f"Pipeline completed with status: {results['status']}")
    
    if results['status'] == 'success':
        logger.info("Pipeline execution successful!")
    else:
        logger.error(f"Pipeline failed: {results.get('message', 'Unknown error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()

# Made with Bob
