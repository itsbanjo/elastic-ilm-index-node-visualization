import logging

# Logging configuration
LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOGGING_LEVEL = logging.INFO

# Required diagnostic files
REQUIRED_FILES = [
    'nodes/nodes_stats.json',
    'nodes/nodes_info.json',
    'indices/indices_stats.json'
]

# Visualization settings
VISUALIZATION_OUTPUT = 'elasticsearch_cluster_visualization.html'
