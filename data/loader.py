import os
import json
import logging
from config import REQUIRED_FILES

logger = logging.getLogger(__name__)

class DataLoader:
    def __init__(self, diagnostics_dir):
        self.diagnostics_dir = diagnostics_dir

    def load_data(self):
        self._check_required_files()
        return self._load_json_files()

    def _check_required_files(self):
        for file in REQUIRED_FILES:
            full_path = os.path.join(self.diagnostics_dir, file)
            if not os.path.exists(full_path):
                logger.error(f"Required file not found: {full_path}")
                raise FileNotFoundError(f"Required file not found: {file}")

    def _load_json_files(self):
        data = {}
        for file in REQUIRED_FILES:
            full_path = os.path.join(self.diagnostics_dir, file)
            try:
                with open(full_path, 'r') as f:
                    file_data = json.load(f)
                    logger.debug(f"Loaded {file}: {type(file_data)}")
                    data[os.path.basename(file)] = file_data
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in file: {full_path}")
                raise

        logger.info("Diagnostic files loaded successfully.")
        logger.debug(f"Loaded data structure: {data.keys()}")
        return data
