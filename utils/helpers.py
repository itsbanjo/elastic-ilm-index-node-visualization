def calculate_memory_usage(node_stats):
    """Calculate memory usage percentage for a node."""
    total_memory = node_stats.get('os', {}).get('mem', {}).get('total_in_bytes', 0)
    used_memory = node_stats.get('os', {}).get('mem', {}).get('used_in_bytes', 0)
    return round((used_memory / total_memory) * 100 if total_memory else 0, 2)

def calculate_disk_usage(node_stats):
    """Calculate disk usage percentage for a node."""
    total_disk = node_stats.get('fs', {}).get('total', {}).get('total_in_bytes', 0)
    free_disk = node_stats.get('fs', {}).get('total', {}).get('free_in_bytes', 0)
    return round((total_disk - free_disk)/total_disk * 100 if total_disk else 0, 2)

def determine_node_type(node_info):
    """Determine the type of a node based on its roles or settings."""
    roles = node_info.get('roles', [])
    settings = node_info.get('settings', {}).get('node', {})
    
    if 'data_hot' in roles or settings.get('attr.data', '') == 'hot':
        return 'hot'
    elif 'data_warm' in roles or settings.get('attr.data', '') == 'warm':
        return 'warm'
    elif 'data_cold' in roles or settings.get('attr.data', '') == 'cold':
        return 'cold'
    elif 'data_frozen' in roles or settings.get('attr.data', '') == 'frozen':
        return 'frozen'
    else:
        return 'hot'  # Default to hot if unable to determine
