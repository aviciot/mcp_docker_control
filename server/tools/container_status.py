"""
Container Status Tool
====================
Get detailed status of a specific container
"""

import logging
import json
from mcp_app import mcp
from utils.docker_client import get_container_by_name_or_id, format_container_info
from utils.audit_logger import log_audit

logger = logging.getLogger(__name__)


@mcp.tool(
    name="container_status",
    description="Get detailed status information for a specific Docker container including state, ports, health, and configuration."
)
def container_status(container_name: str):
    """
    Get detailed status of a Docker container
    
    Args:
        container_name: Container name or ID
    
    Returns:
        str: Detailed container status information
    """
    try:
        # Validate input
        if not container_name:
            return "Error: container_name cannot be empty"
        
        # Get container
        container = get_container_by_name_or_id(container_name)
        
        if not container:
            log_audit(
                operation="get_status",
                container=container_name,
                success=False,
                error="Container not found"
            )
            return f"Error: Container not found: {container_name}"
        
        # Get container info
        info = format_container_info(container)
        
        # Log audit
        log_audit(
            operation="get_status",
            container=container_name,
            success=True
        )
        
        # Format response
        result = f"""Container Status: {info['name']}
=====================================
ID: {info['id']}
Image: {info['image']}
Status: {info['status']}
State: {info['state']['Status']}
Running: {info['state']['Running']}
Paused: {info['state']['Paused']}
Restarting: {info['state']['Restarting']}
OOMKilled: {info['state']['OOMKilled']}
Dead: {info['state']['Dead']}
Pid: {info['state'].get('Pid', 'N/A')}
Exit Code: {info['state'].get('ExitCode', 'N/A')}
Started At: {info['state'].get('StartedAt', 'N/A')}
Finished At: {info['state'].get('FinishedAt', 'N/A')}
"""
        
        # Add ports if available
        if info['ports']:
            result += f"\nPorts:\n"
            for container_port, host_bindings in info['ports'].items():
                if host_bindings:
                    for binding in host_bindings:
                        result += f"  {binding.get('HostIp', '0.0.0.0')}:{binding.get('HostPort')} -> {container_port}\n"
                else:
                    result += f"  {container_port} (not published)\n"
        
        return result
        
    except PermissionError as e:
        logger.warning(f"Permission denied for container {container_name}: {e}")
        log_audit(operation="get_status", container=container_name, success=False, error=str(e))
        return f"Error: {str(e)}"
    except Exception as e:
        logger.exception(f"Error getting container status: {e}")
        log_audit(operation="get_status", container=container_name, success=False, error=str(e))
        return f"Error getting container status: {str(e)}"
