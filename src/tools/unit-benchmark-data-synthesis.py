import os
from common.utils import setup
from tools.unit_benchmark import UnitBenchmarkDataSynthesizer

def main():

    tool = os.path.basename(__file__)
    description = "Synthesize Q&A pairs for the healthcare ChatBot."
    args, logger = setup(tool, description)
    
    synthesizer = UnitBenchmarkDataSynthesizer(
        args.model, args.service_url, args.template_dir, args.data_dir, logger)
    synthesizer.generate_all()

if __name__ == "__main__":
    main()
