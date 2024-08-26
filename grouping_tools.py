import json
import ipaddress
from collections import defaultdict
import re
import logging
import os
import csv
from config import LOGGING_FORMAT, LOGGING_LEVEL, REQUIRED_FILES, VISUALIZATION_OUTPUT
from jinja2 import Template

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

def format_bytes(bytes_value):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0

def calculate_memory_usage(node_stats):
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

def group_nodes(node_stats, node_info):
    groups = defaultdict(list)
    
    for node_id, stats in node_stats['nodes'].items():
        info = node_info['nodes'].get(node_id, {})
        
        ip = stats.get('transport_address', '').split(':')[0]
        hostname = info.get('name', '')
        
        ip_prefix = extract_ip_prefix(ip)
        hostname_prefix = extract_hostname_prefix(hostname)
        
        cpu_usage = stats['os']['cpu']['percent']
        memory_usage = calculate_memory_usage(stats)
        
        total_disk = stats['fs']['total']['total_in_bytes']
        used_disk = total_disk - stats['fs']['total']['available_in_bytes']
        disk_usage = (used_disk / total_disk) * 100
        
        heap_used = stats['jvm']['mem']['heap_used_in_bytes']
        heap_max = stats['jvm']['mem']['heap_max_in_bytes']
        
        group_name = f"{hostname_prefix}-{ip_prefix}"
        groups[group_name].append({
            'node_id': node_id,
            'ip': ip,
            'hostname': hostname,
            'roles': info.get('roles', []),
            'cpu_usage': cpu_usage,
            'memory_usage': memory_usage,
            'disk_usage': disk_usage,
            'disk_used': used_disk,
            'total_disk': total_disk,
            'heap_used': heap_used,
            'heap_max': heap_max
        })
    
    # Calculate group summaries
    for group_name, nodes in groups.items():
        total_memory_used = sum(node['memory_usage']['used'] for node in nodes)
        total_memory = sum(node['memory_usage']['total'] for node in nodes)
        total_disk_used = sum(node['disk_used'] for node in nodes)
        total_disk = sum(node['total_disk'] for node in nodes)
        total_cpu_usage = sum(node['cpu_usage'] for node in nodes)
        node_count = len(nodes)
        
        groups[group_name] = {
            'nodes': nodes,
            'summary': {
                'avg_memory_used': total_memory_used / node_count,
                'avg_total_memory': total_memory / node_count,
                'avg_disk_used': total_disk_used / node_count,
                'avg_total_disk': total_disk / node_count,
                'avg_cpu_usage': total_cpu_usage / node_count
            }
        }
    
    return groups

def generate_html_report(groups):
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ElasticSearch Cluster Report</title>
        <style>
            body { font-family: Arial, sans-serif; }
            table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .summary { background-color: #e6f3ff; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>ElasticSearch Cluster Report</h1>
        {% for group_name, group_data in groups.items() %}
            <h2>Group: {{ group_name }}</h2>
            <table>
                <tr class="summary">
                    <td colspan="16">Group Summary</td>
                </tr>
                <tr class="summary">
                    <td>Avg Memory Used</td>
                    <td>Avg Total Memory</td>
                    <td>Avg Disk Used</td>
                    <td>Avg Total Disk</td>
                    <td>Avg CPU Usage</td>
                </tr>
                <tr class="summary">
                    <td>{{ format_bytes(group_data.summary.avg_memory_used) }}</td>
                    <td>{{ format_bytes(group_data.summary.avg_total_memory) }}</td>
                    <td>{{ format_bytes(group_data.summary.avg_disk_used) }}</td>
                    <td>{{ format_bytes(group_data.summary.avg_total_disk) }}</td>
                    <td>{{ '%.2f'|format(group_data.summary.avg_cpu_usage) }}%</td>
                </tr>
                <tr>
                    <th>Hostname</th>
                    <th>IP</th>
                    <th>Roles</th>
                    <th>CPU Usage (%)</th>
                    <th>Memory Usage (%)</th>
                    <th>Memory Used</th>
                    <th>Total Memory</th>
                    <th>JVM Heap</th>
                    <th>Field Data Cache</th>
                    <th>Query Cache</th>
                    <th>Segment Memory</th>
                    <th>Disk Usage (%)</th>
                    <th>Disk Used</th>
                    <th>Total Disk</th>
                    <th>Heap Used</th>
                    <th>Max Heap</th>
                </tr>
                {% for node in group_data.nodes %}
                <tr>
                    <td>{{ node.hostname }}</td>
                    <td>{{ node.ip }}</td>
                    <td>{{ ', '.join(node.roles) }}</td>
                    <td>{{ '%.2f'|format(node.cpu_usage) }}</td>
                    <td>{{ '%.2f'|format(node.memory_usage.percentage) }}</td>
                    <td>{{ format_bytes(node.memory_usage.used) }}</td>
                    <td>{{ format_bytes(node.memory_usage.total) }}</td>
                    <td>{{ format_bytes(node.memory_usage.jvmHeap) }}</td>
                    <td>{{ format_bytes(node.memory_usage.fieldDataCache) }}</td>
                    <td>{{ format_bytes(node.memory_usage.queryCache) }}</td>
                    <td>{{ format_bytes(node.memory_usage.segmentMemory) }}</td>
                    <td>{{ '%.2f'|format(node.disk_usage) }}</td>
                    <td>{{ format_bytes(node.disk_used) }}</td>
                    <td>{{ format_bytes(node.total_disk) }}</td>
                    <td>{{ format_bytes(node.heap_used) }}</td>
                    <td>{{ format_bytes(node.heap_max) }}</td>
                </tr>
                {% endfor %}
            </table>
        {% endfor %}
    </body>
    </html>
    """
    template = Template(html_template)
    return template.render(groups=groups, format_bytes=format_bytes)

def generate_csv_report(groups):
    csv_data = []
    for group_name, group_data in groups.items():
        csv_data.append(['Group', group_name])
        csv_data.append(['Avg Memory Used', 'Avg Total Memory', 'Avg Disk Used', 'Avg Total Disk', 'Avg CPU Usage'])
        csv_data.append([
            format_bytes(group_data['summary']['avg_memory_used']),
            format_bytes(group_data['summary']['avg_total_memory']),
            format_bytes(group_data['summary']['avg_disk_used']),
            format_bytes(group_data['summary']['avg_total_disk']),
            f"{group_data['summary']['avg_cpu_usage']:.2f}%"
        ])
        csv_data.append([])  # Empty row for separation
        csv_data.append(['Hostname', 'IP', 'Roles', 'CPU Usage (%)', 'Memory Usage (%)', 
                         'Memory Used', 'Total Memory', 'JVM Heap', 'Field Data Cache', 'Query Cache',
                         'Segment Memory', 'Disk Usage (%)', 'Disk Used', 'Total Disk', 
                         'Heap Used', 'Max Heap'])
        for node in group_data['nodes']:
            csv_data.append([
                node['hostname'],
                node['ip'],
                ', '.join(node['roles']),
                f"{node['cpu_usage']:.2f}",
                f"{node['memory_usage']['percentage']:.2f}",
                format_bytes(node['memory_usage']['used']),
                format_bytes(node['memory_usage']['total']),
                format_bytes(node['memory_usage']['jvmHeap']),
                format_bytes(node['memory_usage']['fieldDataCache']),
                format_bytes(node['memory_usage']['queryCache']),
                format_bytes(node['memory_usage']['segmentMemory']),
                f"{node['disk_usage']:.2f}",
                format_bytes(node['disk_used']),
                format_bytes(node['total_disk']),
                format_bytes(node['heap_used']),
                format_bytes(node['heap_max'])
            ])
        csv_data.append([])  # Empty row for separation
    return csv_data
def main():
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

    groups = group_nodes(node_stats, node_info)

    # Generate HTML report
    html_report = generate_html_report(groups)
    with open(VISUALIZATION_OUTPUT, 'w') as f:
        f.write(html_report)
    logger.info(f"HTML report saved to: {VISUALIZATION_OUTPUT}")

    # Generate CSV report
    csv_data = generate_csv_report(groups)
    csv_output = os.path.splitext(VISUALIZATION_OUTPUT)[0] + '.csv'
    with open(csv_output, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)
    logger.info(f"CSV report saved to: {csv_output}")

    # Log summary
    logger.info("\nCluster Summary:")
    for group_name, group_data in groups.items():
        logger.info(f"\nGroup: {group_name}")
        logger.info(f"  Group Summary:")
        logger.info(f"    Avg Memory Used: {format_bytes(group_data['summary']['avg_memory_used'])}")
        logger.info(f"    Avg Total Memory: {format_bytes(group_data['summary']['avg_total_memory'])}")
        logger.info(f"    Avg Disk Used: {format_bytes(group_data['summary']['avg_disk_used'])}")
        logger.info(f"    Avg Total Disk: {format_bytes(group_data['summary']['avg_total_disk'])}")
        logger.info(f"    Avg CPU Usage: {group_data['summary']['avg_cpu_usage']:.2f}%")
        for node in group_data['nodes']:
            logger.info(f"  - Hostname: {node['hostname']}")
            logger.info(f"    IP: {node['ip']}")
            logger.info(f"    Roles: {', '.join(node['roles'])}")
            logger.info(f"    CPU Usage: {node['cpu_usage']:.2f}%")
            logger.info(f"    Memory Usage: {node['memory_usage']['percentage']:.2f}%")
            logger.info(f"    Memory Used: {format_bytes(node['memory_usage']['used'])}")
            logger.info(f"    Total Memory: {format_bytes(node['memory_usage']['total'])}")
            logger.info(f"    JVM Heap: {format_bytes(node['memory_usage']['jvmHeap'])}")
            logger.info(f"    Field Data Cache: {format_bytes(node['memory_usage']['fieldDataCache'])}")
            logger.info(f"    Query Cache: {format_bytes(node['memory_usage']['queryCache'])}")
            logger.info(f"    Segment Memory: {format_bytes(node['memory_usage']['segmentMemory'])}")
            logger.info(f"    Disk Usage: {node['disk_usage']:.2f}%")
            logger.info(f"    Disk Used: {format_bytes(node['disk_used'])}")
            logger.info(f"    Total Disk: {format_bytes(node['total_disk'])}")
            logger.info(f"    Heap Used: {format_bytes(node['heap_used'])}")
            logger.info(f"    Max Heap: {format_bytes(node['heap_max'])}")

if __name__ == "__main__":
    main()
