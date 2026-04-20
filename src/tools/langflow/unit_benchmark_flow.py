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

from common.utils import setup, all_use_cases
from tools.unit_benchmark import UnitBenchmarkDataSynthesizer, UnitBenchmarkDataValidator

class UnitBenchmarkFlowOrchestrator:
    """Orchestrates the benchmark data synthesis and validation pipeline."""
    
    def __init__(
        self,
        model_name: str,
        service_url: str,
        template_dir: str,
        data_dir: str,
        use_case: Optional[str],
        just_synthesis: bool,
        just_validation: bool,
        just_stats: bool,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the flow orchestrator.
        
        Args:
            model_name: The LLM model to use
            service_url: The inference service URL
            template_dir: Directory containing prompt templates
            data_dir: Directory for data files
            use_case: Name of a use case to focus on or None for all of them
            just_stats: In the validation stage, skip validation and only print the stats
            logger: Optional logger instance
        """
        self.model_name = model_name
        self.service_url = service_url
        self.template_dir = template_dir
        self.data_dir = data_dir
        self.just_synthesis = just_synthesis
        self.just_validation = just_validation
        self.just_stats = just_stats
        all_ucs = all_use_cases()
        self.use_cases = [use_case] if use_case else list(all_ucs.keys())
        self.logger = logger or logging.getLogger(__name__)
        
        self.synthesis_results  = None
        self.validation_results = None
        
    def run_synthesis(self) -> Dict[str, Any]:
        """
        Run the data synthesis step.
        
        Args:
            use_case: Optional specific use case to generate. If None, generates all.
            
        Returns:
            Dictionary with synthesis results
        """
        self.logger.info("Starting benchmark data synthesis...")
        
        # Create synthesizer instance.
        synthesizer = UnitBenchmarkDataSynthesizer(
            model_name=self.model_name,
            service_url=self.service_url,
            template_dir=self.template_dir,
            data_dir=self.data_dir,
            use_cases=self.use_cases,
            logger=self.logger
        )
        
        self.synthesis_results = {}
        if len(self.use_cases) == 1:
            # User specified the one use case to run.
            all_ucs = all_use_cases()
            use_case = self.use_cases[0]
            if use_case in all_ucs:
                label = all_ucs[use_case]
                num_unexpected = synthesizer.generate_data_for_use_case(use_case, label)
                self.synthesis_results = {
                    "status": "success",
                    "use_case": use_case,
                    "number_unexpected_labels": num_unexpected,
                    "data_dir": self.data_dir
                }
            else:
                self.synthesis_results = {
                    "status": "error",
                    "message": f"Unknown use case: {use_case}"
                }
        else:
            num_unexpected = synthesizer.generate_data()
            self.synthesis_results = {
                "status": "success",
                "use_case": f"all: {', '.join(self.use_cases)}",
                "number_unexpected_labels": num_unexpected,
                "data_dir": self.data_dir
            }
        
        self.logger.info(f"Synthesis completed: {self.synthesis_results}")
        return self.synthesis_results
    
    def run_validation(self) -> Dict[str, Any]:
        """
        Run the data validation step.
            
        Returns:
            Dictionary with validation results
        """
        self.logger.info("Starting benchmark data validation...")
        
        validator = UnitBenchmarkDataValidator(
            just_stats=self.just_stats,
            model_name=self.model_name,
            service_url=self.service_url,
            template_dir=self.template_dir,
            data_dir=self.data_dir,
            use_cases=self.use_cases,
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
    
    def run_full_pipeline(self) -> Dict[str, Any]:
        """
        Run the complete pipeline: synthesis followed by validation.
            
        Returns:
            Dictionary with complete pipeline results
        """
        self.synthesis_results = {}
        self.logger.info("Starting unit benchmark data pipeline...")
        if self.just_stats:
            self.logger.info("Just calculating statistics; skipping data synthesis...")
            self.synthesis_results = {
                "status": "success",
                "message": "Synthesis skipped; just calculating statistics.",
            }
        elif self.just_validation:
            self.logger.info("Just running validation; skipping data synthesis... (assumes data files already exist!)")
            self.synthesis_results = {
                "status": "success",
                "message": "Synthesis skipped; just running validation.",
            }
        else:
            # Step 1: Synthesis
            self.synthesis_results = self.run_synthesis()
            
            if self.synthesis_results.get("status") != "success":
                return {
                    "status": "error",
                    "message": "Synthesis failed",
                    "synthesis_results": self.synthesis_results
                }
        
        # Step 2: Validation (will handle the self.just_stats flag internally...)
        self.validation_results = {}
        if self.just_synthesis:
            self.validation_results = {
                "status": "success",
                "message": "Just synthesis performed; validation skipped",
            }
        else:
            self.validation_results = self.run_validation()
        
        syn_msg = self.synthesis_results.get('message', 'No synthesis message available!')
        val_msg = self.validation_results.get('message', 'No validation message available!')
        return {
            "status": "success",
            "message": f"Synthesis: {syn_msg} Validation:{val_msg}",
            "synthesis_results": self.synthesis_results,
            "validation_results": self.validation_results
        }

def main():
    """Main entry point for running the benchmark flow."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run benchmark data synthesis and validation pipeline"
    )
    parser.add_argument(
        "-m", "--model",
        default="ollama_chat/gemma4:e4b",
        help="Model name to use"
    )
    parser.add_argument(
        "-s", "--service-url",
        default="http://localhost:11434",
        help="Inference service URL"
    )
    parser.add_argument(
        "-t", "--template-dir",
        default="tools/prompts/templates",
        help="Template directory"
    )
    parser.add_argument(
        "-d", "--data-dir",
        default="data",
        help="Data directory"
    )
    parser.add_argument(
        "-u", "--use-case", nargs="*",
        default=None,
        help="Specific use case to generate (default: all)"
    )

    parser.add_argument(
        "--just-synthesis",
        action="store_true",
        help="Only run the synthesis step."
    )
    parser.add_argument(
        "--just-validation",
        action="store_true",
        help="Only run the validation step. Assumes the synthesized data already exists."
    )
    parser.add_argument(
        "--just-stats",
        action="store_true",
        help="Only compute validation statistics"
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
        use_case=args.use_case,
        just_synthesis=args.just_synthesis,
        just_validation=args.just_validation,
        just_stats=args.just_stats,
        logger=logger
    )
    
    # Run the pipeline
    results = orchestrator.run_full_pipeline()
    
    logger.info(f"Pipeline completed with status: {results['status']}")
    
    if results['status'] == 'success':
        logger.info("Pipeline execution successful!")
    else:
        logger.error(f"Pipeline failed: {results.get('message', 'Unknown error')}")
        sys.exit(1)

if __name__ == "__main__":
    main()

