"""
Container Stats Tool
===================
Get resource usage statistics for containers
"""

import logging
import json
from mcp_app import mcp
from utils.docker_client import get_container_by_name_or_id
from utils.audit_logger import log_audit

logger = logging.getLogger(__name__)


@mcp.tool()
async def get_container_stats(container_name: str) -> str:
    """
    Get resource usage statistics for a Docker container
    
    Args:
        container_name: Container name or ID
    
    Returns:
        str: Container resource usage statistics
    """
    try:
        # Validate input
        if not container_name:
            return "Error: container_name cannot be empty"
        
        # Get container
        container = get_container_by_name_or_id(container_name)
        
        if not container:
            log_audit(
                operation="get_stats",
                container=container_name,
                success=False,
                error="Container not found"
            )
            return f"Error: Container not found: {container_name}"
        
        # Check if container is running
        if container.status != 'running':
            log_audit(
                operation="get_stats",
                container=container_name,
                success=False,
                error="Container not running"
            )
            return f"Error: Cannot get stats for non-running container (status: {container.status})"
        
        # Get stats (stream=False returns a single snapshot)
        stats = container.stats(stream=False)
        
        # Parse CPU usage
        cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
        system_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
        num_cpus = stats['cpu_stats'].get('online_cpus', 1)
        cpu_percent = 0.0
        if system_delta > 0:
            cpu_percent = (cpu_delta / system_delta) * num_cpus * 100.0
        
        # Parse memory usage
        mem_usage = stats['memory_stats'].get('usage', 0)
        mem_limit = stats['memory_stats'].get('limit', 0)
        mem_percent = 0.0
        if mem_limit > 0:
            mem_percent = (mem_usage / mem_limit) * 100.0
        
        # Parse network I/O
        networks = stats.get('networks', {})
        total_rx = sum(net['rx_bytes'] for net in networks.values())
        total_tx = sum(net['tx_bytes'] for net in networks.values())
        
        # Parse block I/O
        block_io = stats.get('blkio_stats', {}).get('io_service_bytes_recursive', [])
        total_read = sum(item['value'] for item in block_io if item['op'] == 'Read')
        total_write = sum(item['value'] for item in block_io if item['op'] == 'Write')
        
        # Log audit
        log_audit(operation="get_stats", container=container_name, success=True)
        
        # Format response
        result = f"""Resource Statistics: {container_name}
=====================================
CPU Usage: {cpu_percent:.2f}%
Memory Usage: {mem_usage / (1024**2):.2f} MB / {mem_limit / (1024**2):.2f} MB ({mem_percent:.2f}%)

Network I/O:
  RX: {total_rx / (1024**2):.2f} MB
  TX: {total_tx / (1024**2):.2f} MB

Block I/O:
  Read: {total_read / (1024**2):.2f} MB
  Write: {total_write / (1024**2):.2f} MB

PIDs: {stats.get('pids_stats', {}).get('current', 'N/A')}
"""
        
        return result
        
    except PermissionError as e:
        logger.warning(f"Permission denied for container {container_name}: {e}")
        log_audit(operation="get_stats", container=container_name, success=False, error=str(e))
        return f"Error: {str(e)}"
    except Exception as e:
        logger.exception(f"Error getting container stats: {e}")
        log_audit(operation="get_stats", container=container_name, success=False, error=str(e))
        return f"Error getting container stats: {str(e)}"
