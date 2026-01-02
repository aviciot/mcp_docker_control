"""
Start Container Tool
===================
Start a stopped Docker container
"""

import logging
from mcp_app import mcp
from utils.docker_client import get_container_by_name_or_id
from utils.audit_logger import log_audit

logger = logging.getLogger(__name__)


@mcp.tool()
async def start_container(container_name: str) -> str:
    """
    Start a stopped Docker container
    
    Args:
        container_name: Container name or ID
    
    Returns:
        str: Success or error message
    """
    try:
        # Validate input
        if not container_name:
            return "Error: container_name cannot be empty"
        
        # Get container
        container = get_container_by_name_or_id(container_name)
        
        if not container:
            log_audit(
                operation="start",
                container=container_name,
                success=False,
                error="Container not found"
            )
            return f"Error: Container not found: {container_name}"
        
        # Check current state
        if container.status == 'running':
            log_audit(operation="start", container=container_name, success=True, details={'already_running': True})
            return f"Container {container_name} is already running"
        
        # Start container
        container.start()
        
        # Log audit
        log_audit(operation="start", container=container_name, success=True)
        
        return f"Successfully started container: {container_name}"
        
    except PermissionError as e:
        logger.warning(f"Permission denied for container {container_name}: {e}")
        log_audit(operation="start", container=container_name, success=False, error=str(e))
        return f"Error: {str(e)}"
    except Exception as e:
        logger.exception(f"Error starting container: {e}")
        log_audit(operation="start", container=container_name, success=False, error=str(e))
        return f"Error starting container: {str(e)}"
