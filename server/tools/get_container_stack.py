"""
Get Container Stack Tool
========================
Identify which Docker Compose stack/project a container belongs to
"""

import logging
from mcp_app import mcp
from utils.docker_client import get_docker_client, get_container_by_name_or_id
from utils.audit_logger import log_audit

logger = logging.getLogger(__name__)


@mcp.tool(
    name="get_container_stack",
    description="Get the Docker Compose project/stack name that a container belongs to, along with all other containers in the same stack."
)
def get_container_stack(container_name: str):
    """
    Get Docker Compose stack information for a container
    
    Args:
        container_name: Container name or ID
    
    Returns:
        str: Stack information or error message
    """
    try:
        # Validate input
        if not container_name:
            return "Error: container_name cannot be empty"
        
        # Get Docker client
        client = get_docker_client()
        if not client:
            return "Error: Unable to connect to Docker"
        
        # Get container
        container = get_container_by_name_or_id(container_name)
        if not container:
            log_audit(operation="get_container_stack", container=container_name, success=False, error="Container not found")
            return f"Error: Container '{container_name}' not found"
        
        # Get compose labels
        labels = container.labels
        project_name = labels.get('com.docker.compose.project')
        service_name = labels.get('com.docker.compose.service')
        project_working_dir = labels.get('com.docker.compose.project.working_dir')
        config_files = labels.get('com.docker.compose.project.config_files')
        
        if not project_name:
            log_audit(operation="get_container_stack", container=container_name, success=True)
            return f"Container '{container_name}' is not part of a Docker Compose stack (no compose labels found)"
        
        # Find all containers in the same stack
        all_containers = client.containers.list(all=True)
        stack_containers = []
        
        for c in all_containers:
            c_project = c.labels.get('com.docker.compose.project')
            if c_project == project_name:
                c_service = c.labels.get('com.docker.compose.service', 'unknown')
                stack_containers.append({
                    'name': c.name,
                    'service': c_service,
                    'status': c.status,
                    'id': c.short_id
                })
        
        # Build response
        result = f"Docker Compose Stack Information\n"
        result += f"=" * 50 + "\n\n"
        result += f"Container: {container.name}\n"
        result += f"Project/Stack: {project_name}\n"
        result += f"Service: {service_name}\n"
        
        if project_working_dir:
            result += f"Working Directory: {project_working_dir}\n"
        
        if config_files:
            result += f"Compose Files: {config_files}\n"
        
        result += f"\nAll containers in stack '{project_name}':\n"
        result += "-" * 50 + "\n"
        
        for sc in sorted(stack_containers, key=lambda x: x['service']):
            status_icon = "🟢" if sc['status'] == 'running' else "🔴"
            result += f"{status_icon} {sc['name']}\n"
            result += f"   Service: {sc['service']}\n"
            result += f"   Status: {sc['status']}\n"
            result += f"   ID: {sc['id']}\n\n"
        
        result += f"\nTotal containers in stack: {len(stack_containers)}\n"
        
        log_audit(operation="get_container_stack", container=container_name, success=True, details={"project": project_name, "containers": len(stack_containers)})
        return result
        
    except Exception as e:
        error_msg = f"Error getting stack info: {str(e)}"
        logger.error(error_msg)
        log_audit(operation="get_container_stack", container=container_name, success=False, error=str(e))
        return error_msg
