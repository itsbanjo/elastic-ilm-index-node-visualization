import json
import logging
from config import VISUALIZATION_OUTPUT

logger = logging.getLogger(__name__)

class VisualizationGenerator:
    def __init__(self, processed_data):
        self.cluster_data = processed_data.get('cluster_data', {})
        self.rolling_indices = processed_data.get('rolling_indices', {})
        self.rolling_indices_size = processed_data.get('rolling_indices_size', {})
        self.all_indices = self._get_all_indices()

    def _get_all_indices(self):
        indices = set()
        for node_type in self.cluster_data.get('children', []):
            for node in node_type.get('children', []):
                for index in node.get('children', []):
                    indices.add(index['name'])
        return sorted(list(indices))

    def generate_visualization(self):
        try:
            logger.debug("Starting visualization generation")
            
            with open('visualization/templates/visualization_template.html', 'r') as template_file:
                template = template_file.read()
            
            logger.debug(f"Template file read, size: {len(template)} characters")

            cluster_data_json = json.dumps(self.cluster_data)
            rolling_indices_json = json.dumps(self.rolling_indices)
            rolling_indices_size_json = json.dumps(self.rolling_indices_size)
            all_indices_json = json.dumps(self.all_indices)

            logger.debug(f"Cluster data size: {len(cluster_data_json)} characters")
            logger.debug(f"Rolling indices data size: {len(rolling_indices_json)} characters")
            logger.debug(f"Rolling indices size data size: {len(rolling_indices_size_json)} characters")
            logger.debug(f"All indices data size: {len(all_indices_json)} characters")

            visualization = template.replace(
                '{{ CLUSTER_DATA }}', cluster_data_json
            ).replace(
                '{{ ROLLING_INDICES }}', rolling_indices_json
            ).replace(
                '{{ ROLLING_INDICES_SIZE }}', rolling_indices_size_json
            ).replace(
                '{{ ALL_INDICES }}', all_indices_json
            )

            logger.debug(f"Placeholders replaced, new visualization size: {len(visualization)} characters")

            with open(VISUALIZATION_OUTPUT, 'w') as output_file:
                output_file.write(visualization)

            logger.info(f"Visualization generated: {VISUALIZATION_OUTPUT}")

        except Exception as e:
            logger.error(f"Error generating visualization: {str(e)}")
            raise

    def validate_data(self):
        if not isinstance(self.cluster_data, dict) or 'name' not in self.cluster_data or 'children' not in self.cluster_data:
            logger.error("Invalid cluster data structure")
            return False
        if not isinstance(self.rolling_indices, dict):
            logger.error("Invalid rolling indices data structure")
            return False
        if not isinstance(self.rolling_indices_size, dict):
            logger.error("Invalid rolling indices size data structure")
            return False
        return True
