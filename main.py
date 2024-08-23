import sys
import logging
import traceback
from data.loader import DataLoader
from data.processor import DataProcessor
from visualization.generator import VisualizationGenerator
from config import LOGGING_FORMAT, LOGGING_LEVEL

logging.basicConfig(level=LOGGING_LEVEL, format=LOGGING_FORMAT)
logger = logging.getLogger(__name__)

def main(diagnostics_dir):
    try:
        # Load data
        loader = DataLoader(diagnostics_dir)
        raw_data = loader.load_data()
        logger.debug(f"Raw data loaded: {type(raw_data)}")
        logger.debug(f"Raw data keys: {raw_data.keys()}")

        # Process data
        processor = DataProcessor(raw_data)
        processed_data = processor.process_data()
        logger.debug(f"Processed data: {type(processed_data)}")
        logger.debug(f"Processed data keys: {processed_data.keys()}")

        # Generate visualization
        generator = VisualizationGenerator(processed_data)
        if generator.validate_data():
            generator.generate_visualization()
            logger.info("Visualization generated successfully.")
        else:
            logger.error("Data validation failed. Visualization not generated.")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        logger.error("Traceback:")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <path_to_diagnostics_directory>")
        sys.exit(1)

    diagnostics_dir = sys.argv[1]
    main(diagnostics_dir)
