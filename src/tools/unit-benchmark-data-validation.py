import os
import sys
from common.utils import setup
from tools.unit_benchmark import UnitBenchmarkDataValidator

def main():

    tool = os.path.basename(__file__)
    description = "Validate synthesized Q&A pairs for the healthcare ChatBot."
    args, logger = setup(tool, description, 
        add_arguments = lambda p: p.add_argument("-j", "--just-stats", 
            action='store_true', 
            default=False, 
            help="Just report the final statistics for existing validation data. Default: False"))

    validator = UnitBenchmarkDataValidator(
        args.model, args.service_url, args.template_dir, args.data_dir, args.use_cases, args.just_stats, logger)
     
    total_stats = validator.validate()
    validator.print_stats(total_stats)

if __name__ == "__main__":
    main()
