"""
List Containers Tool
===================
List all Docker containers with filtering support
"""

import logging
from mcp_app import mcp
from utils.docker_client import get_docker_client, filter_containers, format_container_info
from utils.audit_logger import log_audit

logger = logging.getLogger(__name__)


@mcp.tool()
async def list_containers(all_containers: bool = False) -> str:
    """
    List Docker containers
    
    Args:
        all_containers: If True, include stopped containers. If False, only running containers.
    
    Returns:
        str: Formatted list of containers
    """
    try:
        # Get Docker client
        client = get_docker_client()
        
        # List containers
        containers = client.containers.list(all=all_containers)
        
        # Filter containers based on whitelist/blacklist
        containers = filter_containers(containers)
        
        # Log audit
        log_audit(
            operation="list_containers",
            success=True,
            details={'all_containers': all_containers, 'count': len(containers)}
        )
        
        if not containers:
            return "No containers found"
        
        # Format container information
        result = []
        for container in containers:
            info = format_container_info(container)
            result.append(
                f"Container: {info['name']}\n"
                f"  ID: {info['id']}\n"
                f"  Image: {info['image']}\n"
                f"  Status: {info['status']}\n"
                f"  State: {info['state']['Status']}\n"
            )
        
        return "\n".join(result)
        
    except Exception as e:
        logger.exception(f"Error listing containers: {e}")
        log_audit(operation="list_containers", success=False, error=str(e))
        return f"Error listing containers: {str(e)}"
