"""
Container Logs Tool
==================
Get logs from a Docker container
"""

import logging
from mcp_app import mcp
from utils.docker_client import get_container_by_name_or_id
from utils.audit_logger import log_audit

logger = logging.getLogger(__name__)


@mcp.tool(
    name="get_container_logs",
    description="Retrieve logs from a Docker container with options for tail lines, since timestamp, and timestamp display."
)
def get_container_logs(
    container_name: str,
    tail: int = 100,
    since: str = "",
    timestamps: bool = False
):
    """
    Get logs from a Docker container
    
    Args:
        container_name: Container name or ID
        tail: Number of lines to show from end of logs (default: 100, use 0 for all)
        since: Only return logs since this time (e.g., "2024-01-01T00:00:00" or "1h")
        timestamps: Include timestamps in log output
    
    Returns:
        str: Container logs
    """
    try:
        # Validate input
        if not container_name:
            return "Error: container_name cannot be empty"
        
        if tail < 0:
            return "Error: tail must be >= 0"
        
        # Get container
        container = get_container_by_name_or_id(container_name)
        
        if not container:
            log_audit(
                operation="get_logs",
                container=container_name,
                success=False,
                error="Container not found"
            )
            return f"Error: Container not found: {container_name}"
        
        # Get logs
        kwargs = {
            'timestamps': timestamps,
            'stdout': True,
            'stderr': True,
        }
        
        if tail > 0:
            kwargs['tail'] = tail
        else:
            kwargs['tail'] = 'all'
        
        if since:
            kwargs['since'] = since
        
        logs = container.logs(**kwargs).decode('utf-8')
        
        # Log audit
        log_audit(
            operation="get_logs",
            container=container_name,
            success=True,
            details={'tail': tail, 'since': since}
        )
        
        if not logs:
            return f"No logs available for container: {container_name}"
        
        return f"Logs for {container_name}:\n{'=' * 50}\n{logs}"
        
    except PermissionError as e:
        logger.warning(f"Permission denied for container {container_name}: {e}")
        log_audit(operation="get_logs", container=container_name, success=False, error=str(e))
        return f"Error: {str(e)}"
    except Exception as e:
        logger.exception(f"Error getting container logs: {e}")
        log_audit(operation="get_logs", container=container_name, success=False, error=str(e))
        return f"Error getting container logs: {str(e)}"
