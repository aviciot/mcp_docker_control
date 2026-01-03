"""
Help Tool
=========
Show all available Docker Control MCP tools with usage examples
"""

import logging
from mcp_app import mcp

logger = logging.getLogger(__name__)


@mcp.tool(
    name="help",
    description="Show all available Docker Control MCP tools with usage examples and syntax."
)
def help(tool_name: str = ""):
    """
    Display help information for all tools or a specific tool
    
    Args:
        tool_name: Optional - specific tool name to get detailed help (leave empty for all tools)
    
    Returns:
        str: Help information
    """
    
    tools_help = {
        # READ-ONLY TOOLS (No password needed)
        "list_stacks": {
            "category": "Read-Only",
            "description": "Show all Docker Compose stacks/projects with summary (FASTEST for stack overview)",
            "parameters": "None",
            "examples": [
                "Show me all stacks",
                "What stacks are running?",
                "List all Docker Compose projects",
                "Show available stacks"
            ],
            "syntax": "list_stacks()"
        },
        
        "list_containers": {
            "category": "Read-Only",
            "description": "List all Docker containers individually",
            "parameters": "all_containers (bool, default=False)",
            "examples": [
                "Show me all containers",
                "List running containers",
                "What containers are running?",
                "Show all containers including stopped ones"
            ],
            "syntax": "list_containers(all_containers=True)"
        },
        
        "container_status": {
            "category": "Read-Only",
            "description": "Get detailed status of a specific container",
            "parameters": "container_name (required)",
            "examples": [
                "What's the status of omni2-bridge?",
                "Show me details about docker-control-mcp container",
                "Get info for container XYZ"
            ],
            "syntax": "container_status(container_name='omni2-bridge')"
        },
        
        "get_container_logs": {
            "category": "Read-Only",
            "description": "View container logs",
            "parameters": "container_name (required), tail (default=100), since (optional), timestamps (default=False)",
            "examples": [
                "Show logs for omni2-bridge",
                "Get last 50 lines from omni2-app logs",
                "Show logs from omni2-bridge since 5 minutes ago",
                "Get logs with timestamps for container X"
            ],
            "syntax": "get_container_logs(container_name='omni2-bridge', tail=50, timestamps=True)"
        },
        
        "container_stats": {
            "category": "Read-Only",
            "description": "Get CPU, memory, network stats for a container",
            "parameters": "container_name (required)",
            "examples": [
                "Show CPU usage for omni2-bridge",
                "What's the memory usage of container X?",
                "Get stats for omni2-app",
                "How much resources is docker-control-mcp using?"
            ],
            "syntax": "container_stats(container_name='omni2-bridge')"
        },
        
        "check_containers_health": {
            "category": "Read-Only",
            "description": "Check health status of all containers with health checks",
            "parameters": "None",
            "examples": [
                "Check health of all containers",
                "Which containers are healthy?",
                "Show container health status",
                "Are all containers healthy?"
            ],
            "syntax": "check_containers_health()"
        },
        
        "get_container_stack": {
            "category": "Read-Only",
            "description": "Show which Docker Compose stack a container belongs to",
            "parameters": "container_name (required)",
            "examples": [
                "What stack does omni2-bridge belong to?",
                "Show me all containers in the same stack as omni2-app",
                "Which project is container X part of?",
                "List all containers in omni2 stack"
            ],
            "syntax": "get_container_stack(container_name='omni2-bridge')"
        },
        
        "compose_status": {
            "category": "Read-Only",
            "description": "Get status of Docker Compose services",
            "parameters": "project_path (required)",
            "examples": [
                "Show status of omni2 compose project",
                "What's running in /path/to/project?",
                "Get compose status for omni2"
            ],
            "syntax": "compose_status(project_path='C:/path/to/omni2')"
        },
        
        # CONTROL TOOLS (Password required)
        "start_container": {
            "category": "Control (Password Required)",
            "description": "Start a stopped container",
            "parameters": "container_name (required), password (required)",
            "examples": [
                "Start container omni2-app with password avicohen",
                "Start the database container, password is avicohen",
                "Turn on container X using password avicohen"
            ],
            "syntax": "start_container(container_name='omni2-app', password='avicohen')"
        },
        
        "stop_container": {
            "category": "Control (Password Required)",
            "description": "Stop a running container",
            "parameters": "container_name (required), password (required), timeout (default=10)",
            "examples": [
                "Stop container omni2-app with password avicohen",
                "Shut down the database container, password avicohen",
                "Stop container X with 30 second timeout, password avicohen"
            ],
            "syntax": "stop_container(container_name='omni2-app', password='avicohen', timeout=30)"
        },
        
        "restart_container": {
            "category": "Control (Password Required)",
            "description": "Restart a container",
            "parameters": "container_name (required), password (required), timeout (default=10)",
            "examples": [
                "Restart omni2-bridge with password avicohen",
                "Reboot container X, password is avicohen",
                "Restart the app container using password avicohen"
            ],
            "syntax": "restart_container(container_name='omni2-bridge', password='avicohen')"
        },
        
        "restart_stack": {
            "category": "Control (Password Required)",
            "description": "Restart ALL containers in a Docker Compose stack",
            "parameters": "container_name (any container in stack), password (required), timeout (default=10)",
            "examples": [
                "Restart the entire omni2 stack with password avicohen",
                "Restart all containers in the same stack as omni2-bridge, password avicohen",
                "Reboot the whole application stack, password is avicohen",
                "Restart the stack that omni2-app belongs to with password avicohen"
            ],
            "syntax": "restart_stack(container_name='omni2-bridge', password='avicohen')"
        }
    }
    
    # If specific tool requested
    if tool_name:
        if tool_name not in tools_help:
            return f"Tool '{tool_name}' not found. Use help() without parameters to see all available tools."
        
        tool = tools_help[tool_name]
        result = f"\n{'='*60}\n"
        result += f"Tool: {tool_name}\n"
        result += f"{'='*60}\n\n"
        result += f"Category: {tool['category']}\n"
        result += f"Description: {tool['description']}\n\n"
        result += f"Parameters:\n  {tool['parameters']}\n\n"
        result += f"Syntax:\n  {tool['syntax']}\n\n"
        result += f"Example Prompts:\n"
        for i, example in enumerate(tool['examples'], 1):
            result += f"  {i}. \"{example}\"\n"
        result += f"\n{'='*60}\n"
        return result
    
    # Show all tools
    result = f"\n{'='*60}\n"
    result += "DOCKER CONTROL MCP - ALL AVAILABLE TOOLS\n"
    result += f"{'='*60}\n\n"
    
    # Group by category
    read_only = {k: v for k, v in tools_help.items() if v['category'] == 'Read-Only'}
    control = {k: v for k, v in tools_help.items() if 'Password Required' in v['category']}
    
    result += "📋 READ-ONLY TOOLS (No password needed):\n"
    result += "-" * 60 + "\n"
    for i, (name, tool) in enumerate(read_only.items(), 1):
        result += f"\n{i}. {name}\n"
        result += f"   {tool['description']}\n"
        result += f"   Example: \"{tool['examples'][0]}\"\n"
    
    result += f"\n\n🔐 CONTROL TOOLS (Password required: avicohen):\n"
    result += "-" * 60 + "\n"
    for i, (name, tool) in enumerate(control.items(), 1):
        result += f"\n{i}. {name}\n"
        result += f"   {tool['description']}\n"
        result += f"   Example: \"{tool['examples'][0]}\"\n"
    
    result += f"\n\n{'='*60}\n"
    result += "💡 TIP: Use help('tool_name') for detailed info\n"
    result += "   Example: help('restart_stack')\n"
    result += f"{'='*60}\n"
    
    return result
