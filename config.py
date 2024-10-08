import logging

# Logging configuration
LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOGGING_LEVEL = logging.INFO

# Required diagnostic files
REQUIRED_FILES = [
    'nodes_stats.json',
    'nodes.json',
    'indices_stats.json'
]

# Visualization settings
VISUALIZATION_OUTPUT = 'report/elasticsearch_cluster_visualization.html'
