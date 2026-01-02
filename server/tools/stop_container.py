"""
Stop Container Tool
==================
Stop a running Docker container
"""

import logging
from mcp_app import mcp
from utils.docker_client import get_container_by_name_or_id
from utils.audit_logger import log_audit

logger = logging.getLogger(__name__)


@mcp.tool(
    name="stop_container",
    description="Stop a running Docker container gracefully with configurable timeout. Requires full-control permission level and password verification."
)
def stop_container(container_name: str, password: str, timeout: int = 10):
    """
    Stop a running Docker container
    
    Args:
        container_name: Container name or ID
        timeout: Seconds to wait before killing container (default: 10)
    
    Returns:
        str: Success or error message
    """
    try:
        # Validate password first
        import os
        expected_password = os.getenv('AUTH_PASSWORD', '')
        if not password or password != expected_password:
            log_audit(operation="stop_container", container=container_name, success=False, error="Invalid or missing password")
            return "Error: Invalid or missing password. Authentication required for this operation."
        
        # Validate input
        if not container_name:
            return "Error: container_name cannot be empty"
        
        if timeout < 0:
            return "Error: timeout must be >= 0"
        
        # Get container
        container = get_container_by_name_or_id(container_name)
        
        if not container:
            log_audit(
                operation="stop",
                container=container_name,
                success=False,
                error="Container not found"
            )
            return f"Error: Container not found: {container_name}"
        
        # Check current state
        if container.status != 'running':
            log_audit(operation="stop", container=container_name, success=True, details={'already_stopped': True})
            return f"Container {container_name} is not running (status: {container.status})"
        
        # Stop container
        container.stop(timeout=timeout)
        
        # Log audit
        log_audit(operation="stop", container=container_name, success=True, details={'timeout': timeout})
        
        return f"Successfully stopped container: {container_name}"
        
    except PermissionError as e:
        logger.warning(f"Permission denied for container {container_name}: {e}")
        log_audit(operation="stop", container=container_name, success=False, error=str(e))
        return f"Error: {str(e)}"
    except Exception as e:
        logger.exception(f"Error stopping container: {e}")
        log_audit(operation="stop", container=container_name, success=False, error=str(e))
        return f"Error stopping container: {str(e)}"
