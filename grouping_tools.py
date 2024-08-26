import json
import ipaddress
from collections import defaultdict
import re
import logging
import os
import argparse
from config import LOGGING_FORMAT, LOGGING_LEVEL, REQUIRED_FILES, VISUALIZATION_OUTPUT

# Set up logging
logging.basicConfig(format=LOGGING_FORMAT, level=LOGGING_LEVEL)
logger = logging.getLogger(__name__)

def load_json(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return None
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in file: {file_path}")
        return None

def extract_ip_prefix(ip_address):
    try:
        return '.'.join(str(ipaddress.ip_address(ip_address)).split('.')[:3])
    except ValueError:
        logger.warning(f"Invalid IP address: {ip_address}")
        return ''

def extract_hostname_prefix(hostname):
    match = re.match(r'^([a-zA-Z]+)', hostname)
    return match.group(1) if match else ''

def is_ignored_node(node_info):
    roles = node_info.get('roles', [])
    
    if 'kibana' in roles or 'master' in roles or 'ml' in roles:
        return True
    
    if node_info.get('attributes', {}).get('kibana.connected', 'false').lower() == 'true':
        return True
    
    return False

def group_nodes(node_stats, node_info):
    groups = defaultdict(list)
    
    for node_id, stats in node_stats['nodes'].items():
        info = node_info['nodes'].get(node_id, {})
        
        if is_ignored_node(info):
            logger.info(f"Ignoring node {node_id} (type: {'Kibana' if 'kibana' in info.get('roles', []) else 'master' if 'master' in info.get('roles', []) else 'ML'})")
            continue
        
        ip = stats.get('transport_address', '').split(':')[0]
        hostname = info.get('name', '')
        
        ip_prefix = extract_ip_prefix(ip)
        hostname_prefix = extract_hostname_prefix(hostname)
        
        group_name = f"{hostname_prefix}-{ip_prefix}"
        groups[group_name].append({
            'node_id': node_id,
            'ip': ip,
            'hostname': hostname,
            'roles': info.get('roles', [])
        })
    
    return groups

def display_node_roles(node_info):
    logger.info("\nNode Roles Configuration:")
    for node_id, info in node_info['nodes'].items():
        roles = info.get('roles', [])
        logger.info(f"Node ID: {node_id}")
        logger.info(f"  Hostname: {info.get('name', 'N/A')}")
        logger.info(f"  Roles: {', '.join(roles) if roles else 'No roles assigned'}")
        logger.info(f"  Is Kibana: {'Yes' if 'kibana' in roles or info.get('attributes', {}).get('kibana.connected', 'false').lower() == 'true' else 'No'}")
        logger.info(f"  Is Master: {'Yes' if 'master' in roles else 'No'}")
        logger.info(f"  Is Data: {'Yes' if 'data' in roles else 'No'}")
        logger.info(f"  Is Ingest: {'Yes' if 'ingest' in roles else 'No'}")
        logger.info(f"  Is Machine Learning: {'Yes' if 'ml' in roles else 'No'}")
        logger.info("  ---")

def main(show_roles):
    for file_path in REQUIRED_FILES:
        if not os.path.exists(file_path):
            logger.error(f"Required file not found: {file_path}")
            return

    node_stats = load_json(REQUIRED_FILES[0])
    node_info = load_json(REQUIRED_FILES[1])
    indices_stats = load_json(REQUIRED_FILES[2])

    if not all([node_stats, node_info, indices_stats]):
        logger.error("Failed to load one or more required files")
        return

    if show_roles:
        display_node_roles(node_info)
        return

    groups = group_nodes(node_stats, node_info)

    logger.info("Node Groups:")
    for group_name, nodes in groups.items():
        logger.info(f"\nGroup: {group_name}")
        for node in nodes:
            logger.info(f"  - Node ID: {node['node_id']}")
            logger.info(f"    IP: {node['ip']}")
            logger.info(f"    Hostname: {node['hostname']}")
            logger.info(f"    Roles: {', '.join(node['roles'])}")

    logger.info(f"Visualization will be saved to: {VISUALIZATION_OUTPUT}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ElasticSearch Node Grouping Tool")
    parser.add_argument("--show-roles", action="store_true", help="Display the configuration of node roles")
    args = parser.parse_args()

    main(args.show_roles)
