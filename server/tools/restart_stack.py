"""
Restart Stack Tool
==================
Restart all containers in a Docker Compose stack
"""

import logging
from mcp_app import mcp
from utils.docker_client import get_docker_client, get_container_by_name_or_id
from utils.audit_logger import log_audit

logger = logging.getLogger(__name__)


@mcp.tool(
    name="restart_stack",
    description="Restart all containers in a Docker Compose stack/project by identifying the stack from any container name. Requires full-control permission and password verification."
)
def restart_stack(container_name: str, password: str, timeout: int = 10):
    """
    Restart entire Docker Compose stack
    
    Args:
        container_name: Name or ID of any container in the stack
        password: Authentication password
        timeout: Seconds to wait for stop before killing (default: 10)
    
    Returns:
        str: Success or error message
    """
    try:
        # Validate password first
        import os
        expected_password = os.getenv('AUTH_PASSWORD', '')
        
        # Debug logging for password validation
        logger.info(f"RESTART_STACK SECURITY CHECK - Container: {container_name}, Password provided: {'YES' if password else 'NO'}, Password length: {len(password) if password else 0}, Expected length: {len(expected_password)}, Match: {password == expected_password if password else False}")
        
        if not password or password != expected_password:
            log_audit(operation="restart_stack", container=container_name, success=False, error="Invalid or missing password")
            return "Error: Invalid or missing password. Authentication required for this operation."
        
        # Validate input
        if not container_name:
            return "Error: container_name cannot be empty"
        
        # Get Docker client
        client = get_docker_client()
        if not client:
            return "Error: Unable to connect to Docker"
        
        # Get container to find its stack
        container = get_container_by_name_or_id(container_name)
        if not container:
            log_audit(operation="restart_stack", container=container_name, success=False, error="Container not found")
            return f"Error: Container '{container_name}' not found"
        
        # Get compose project name
        project_name = container.labels.get('com.docker.compose.project')
        if not project_name:
            log_audit(operation="restart_stack", container=container_name, success=False, error="Not a compose stack")
            return f"Error: Container '{container_name}' is not part of a Docker Compose stack"
        
        # Find all containers in the same stack
        all_containers = client.containers.list(all=True)
        stack_containers = []
        
        for c in all_containers:
            c_project = c.labels.get('com.docker.compose.project')
            if c_project == project_name:
                stack_containers.append(c)
        
        if not stack_containers:
            return f"Error: No containers found in stack '{project_name}'"
        
        # Restart all containers in the stack
        result = f"Restarting Docker Compose stack: {project_name}\n"
        result += "=" * 50 + "\n\n"
        
        restarted = []
        errors = []
        
        for c in stack_containers:
            try:
                service_name = c.labels.get('com.docker.compose.service', 'unknown')
                result += f"Restarting {c.name} (service: {service_name})... "
                
                c.restart(timeout=timeout)
                restarted.append(c.name)
                result += "✅ Success\n"
                
            except Exception as e:
                errors.append(f"{c.name}: {str(e)}")
                result += f"❌ Failed: {str(e)}\n"
        
        result += "\n" + "=" * 50 + "\n"
        result += f"Summary:\n"
        result += f"  Total containers: {len(stack_containers)}\n"
        result += f"  Successfully restarted: {len(restarted)}\n"
        result += f"  Errors: {len(errors)}\n"
        
        if errors:
            result += "\nErrors:\n"
            for error in errors:
                result += f"  - {error}\n"
        
        success = len(errors) == 0
        log_audit(
            operation="restart_stack",
            container=container_name,
            success=success,
            details={
                "project": project_name,
                "total": len(stack_containers),
                "restarted": len(restarted),
                "errors": len(errors)
            }
        )
        
        return result
        
    except Exception as e:
        error_msg = f"Error restarting stack: {str(e)}"
        logger.error(error_msg)
        log_audit(operation="restart_stack", container=container_name, success=False, error=str(e))
        return error_msg
