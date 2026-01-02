"""
List Docker Compose Stacks Tool
================================
Show all Docker Compose stacks/projects with their containers
"""

import logging
from mcp_app import mcp
from utils.docker_client import get_docker_client

logger = logging.getLogger(__name__)


@mcp.tool(
    name="list_stacks",
    description="Show all Docker Compose stacks/projects running on the system with container counts and status summary. Much faster than listing individual containers when you want stack-level overview."
)
def list_stacks():
    """
    List all Docker Compose stacks/projects
    
    Returns:
        str: Summary of all stacks with their containers
    """
    try:
        # Get Docker client
        client = get_docker_client()
        if not client:
            return "Error: Unable to connect to Docker"
        
        # Get all containers
        all_containers = client.containers.list(all=True)
        
        # Group containers by compose project
        stacks = {}
        standalone_containers = []
        
        for container in all_containers:
            project_name = container.labels.get('com.docker.compose.project')
            
            if project_name:
                if project_name not in stacks:
                    stacks[project_name] = {
                        'containers': [],
                        'running': 0,
                        'stopped': 0,
                        'working_dir': container.labels.get('com.docker.compose.project.working_dir', 'N/A'),
                        'config_files': container.labels.get('com.docker.compose.project.config_files', 'N/A')
                    }
                
                stacks[project_name]['containers'].append({
                    'name': container.name,
                    'service': container.labels.get('com.docker.compose.service', 'unknown'),
                    'status': container.status
                })
                
                if container.status == 'running':
                    stacks[project_name]['running'] += 1
                else:
                    stacks[project_name]['stopped'] += 1
            else:
                # Standalone container (not part of compose)
                standalone_containers.append({
                    'name': container.name,
                    'status': container.status
                })
        
        # Build response
        if not stacks and not standalone_containers:
            return "No containers found on the system."
        
        result = "=" * 60 + "\n"
        result += "DOCKER COMPOSE STACKS SUMMARY\n"
        result += "=" * 60 + "\n\n"
        
        if stacks:
            result += f"Found {len(stacks)} Docker Compose stack(s):\n\n"
            
            for project_name in sorted(stacks.keys()):
                stack = stacks[project_name]
                total = stack['running'] + stack['stopped']
                status_icon = "🟢" if stack['stopped'] == 0 else "🟡" if stack['running'] > 0 else "🔴"
                
                result += f"{status_icon} Stack: {project_name}\n"
                result += f"   Total containers: {total}\n"
                result += f"   Running: {stack['running']} | Stopped: {stack['stopped']}\n"
                result += f"   Location: {stack['working_dir']}\n"
                result += f"   Services:\n"
                
                for container in sorted(stack['containers'], key=lambda x: x['service']):
                    c_icon = "🟢" if container['status'] == 'running' else "🔴"
                    result += f"      {c_icon} {container['service']} ({container['name']}) - {container['status']}\n"
                
                result += "\n"
        
        if standalone_containers:
            result += f"Standalone containers (not part of compose): {len(standalone_containers)}\n"
            for container in sorted(standalone_containers, key=lambda x: x['name']):
                c_icon = "🟢" if container['status'] == 'running' else "🔴"
                result += f"   {c_icon} {container['name']} - {container['status']}\n"
        
        result += "\n" + "=" * 60 + "\n"
        result += "💡 TIP: Use restart_stack(container_name, password) to restart an entire stack\n"
        result += "=" * 60 + "\n"
        
        return result
        
    except Exception as e:
        error_msg = f"Error listing stacks: {str(e)}"
        logger.error(error_msg)
        return error_msg
