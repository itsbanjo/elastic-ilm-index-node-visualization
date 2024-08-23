import logging
from utils.helpers import calculate_disk_usage, determine_node_type

logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self, raw_data):
        self.raw_data = raw_data
        self.cluster_data = {"name": "Cluster", "children": []}
        self.rolling_indices = {}
        self.rolling_indices_size = {}
        self.max_indices_per_node = 1000  # Limit the number of indices shown per node
        self.min_index_size_to_show = 1  # Minimum size in MB to show an index individually

    def process_data(self):
        logger.debug(f"Processing data. Raw data keys: {self.raw_data.keys()}")
        self._process_nodes()
        self._process_indices()
        return {
            "cluster_data": self.cluster_data,
            "rolling_indices": self.rolling_indices,
            "rolling_indices_size": self.rolling_indices_size
        }

    def _process_nodes(self):
        node_types = {"hot": [], "warm": [], "cold": [], "frozen": []}
        nodes_stats = self.raw_data['nodes_stats.json'].get('nodes', {})
        nodes_info = self.raw_data['nodes_info.json'].get('nodes', {})
        
        logger.debug(f"Processing nodes. Stats keys: {nodes_stats.keys()}, Info keys: {nodes_info.keys()}")

        for node_id, node_info in nodes_info.items():
            node_stats = nodes_stats.get(node_id, {})
            node_type = determine_node_type(node_info)
            memory_usage = self._calculate_memory_usage(node_stats)
            node_data = {
                "name": node_info.get('name', 'Unknown'),
                "diskUsage": calculate_disk_usage(node_stats),
                "diskTotal": node_stats.get('fs', {}).get('total', {}).get('total_in_bytes', 0),
                "memoryUsage": memory_usage['percentage'],
                "memoryTotal": memory_usage['total'],
                "cpuUsage": node_stats.get('os', {}).get('cpu', {}).get('percent', 0),
                "cpuFree": 100 - node_stats.get('os', {}).get('cpu', {}).get('percent', 0),
                "memoryDetails": memory_usage,
                "children": self._get_node_indices(node_id)
            }
            node_types[node_type].append(node_data)

        for node_type, nodes in node_types.items():
            if nodes:
                self.cluster_data["children"].append({
                    "name": f"{node_type.capitalize()} Nodes",
                    "children": nodes
                })

    def _calculate_memory_usage(self, node_stats):
        total = node_stats.get('os', {}).get('mem', {}).get('total_in_bytes', 0)
        jvm_heap = node_stats.get('jvm', {}).get('mem', {}).get('heap_used_in_bytes', 0)
        field_data_cache = node_stats.get('indices', {}).get('fielddata', {}).get('memory_size_in_bytes', 0)
        query_cache = node_stats.get('indices', {}).get('query_cache', {}).get('memory_size_in_bytes', 0)
        segment_memory = node_stats.get('indices', {}).get('segments', {}).get('memory_in_bytes', 0)
        
        used = jvm_heap + field_data_cache + query_cache + segment_memory
        percentage = (used / total) * 100 if total > 0 else 0
        
        return {
            "total": total,
            "jvmHeap": jvm_heap,
            "fieldDataCache": field_data_cache,
            "queryCache": query_cache,
            "segmentMemory": segment_memory,
            "used": used,
            "percentage": round(percentage, 2)
        }

    def _get_node_indices(self, node_id):
        node_indices = []
        other_indices = {"name": "Other Indices", "size": 0, "count": 0}
        indices_stats = self.raw_data['indices_stats.json'].get('indices', {})
        
        for index_name, index_stats in indices_stats.items():
            shards = index_stats.get('shards', {})
            for shard_id, shard_data in shards.items():
                if isinstance(shard_data, list):
                    shard = next((s for s in shard_data if s.get('routing', {}).get('node') == node_id), None)
                elif isinstance(shard_data, dict):
                    shard = shard_data if shard_data.get('routing', {}).get('node') == node_id else None
                else:
                    continue

                if shard:
                    size = shard.get('store', {}).get('size_in_bytes', 0) / (1024 * 1024)  # Convert to MB
                    if size >= self.min_index_size_to_show and len(node_indices) < self.max_indices_per_node:
                        index_data = {
                            "name": index_name,
                            "size": round(size, 2),
                            "rollingIndex": self._determine_rolling_index(index_name)
                        }
                        node_indices.append(index_data)
                    else:
                        other_indices["size"] += size
                        other_indices["count"] += 1
                    break  # We only need one shard to represent the index on this node

        if other_indices["count"] > 0:
            other_indices["size"] = round(other_indices["size"], 2)
            node_indices.append(other_indices)

        return node_indices

    def _determine_rolling_index(self, index_name):
        parts = index_name.split('-')
        if len(parts) > 1 and parts[-1].isdigit():
            rolling_index = '-'.join(parts[:-1])
            if rolling_index not in self.rolling_indices:
                self.rolling_indices[rolling_index] = []
                self.rolling_indices_size[rolling_index] = 0
            self.rolling_indices[rolling_index].append(index_name)
            return rolling_index
        return None

    def _process_indices(self):
        indices_stats = self.raw_data['indices_stats.json'].get('indices', {})
        for index_name, index_stats in indices_stats.items():
            size = index_stats.get('total', {}).get('store', {}).get('size_in_bytes', 0) / (1024 * 1024)  # Convert to MB
            rolling_index = self._determine_rolling_index(index_name)
            if rolling_index:
                self.rolling_indices_size[rolling_index] += size

        # Round the sizes
        for rolling_index in self.rolling_indices_size:
            self.rolling_indices_size[rolling_index] = round(self.rolling_indices_size[rolling_index], 2)
