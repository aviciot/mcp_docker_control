"""
Restart Container Tool
=====================
Restart a Docker container
"""

import logging
from mcp_app import mcp
from utils.docker_client import get_container_by_name_or_id
from utils.audit_logger import log_audit

logger = logging.getLogger(__name__)


@mcp.tool(
    name="restart_container",
    description="Restart a Docker container gracefully with configurable timeout. Requires full-control permission level and password verification."
)
def restart_container(container_name: str, password: str, timeout: int = 10):
    """
    Restart a Docker container
    
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
        
        # LOG PASSWORD CHECK FOR DEBUGGING
        logger.info(f"RESTART SECURITY CHECK - Container: {container_name}, Password provided: {'YES' if password else 'NO'}, Password length: {len(password) if password else 0}, Match: {password == expected_password if password else False}")
        
        if not password or password != expected_password:
            log_audit(operation="restart_container", container=container_name, success=False, error="Invalid or missing password")
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
                operation="restart",
                container=container_name,
                success=False,
                error="Container not found"
            )
            return f"Error: Container not found: {container_name}"
        
        # Restart container
        container.restart(timeout=timeout)
        
        # Log audit
        log_audit(operation="restart", container=container_name, success=True, details={'timeout': timeout})
        
        return f"Successfully restarted container: {container_name}"
        
    except PermissionError as e:
        logger.warning(f"Permission denied for container {container_name}: {e}")
        log_audit(operation="restart", container=container_name, success=False, error=str(e))
        return f"Error: {str(e)}"
    except Exception as e:
        logger.exception(f"Error restarting container: {e}")
        log_audit(operation="restart", container=container_name, success=False, error=str(e))
        return f"Error restarting container: {str(e)}"
