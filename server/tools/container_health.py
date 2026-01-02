"""
Container Health Tool
====================
Get health check status of containers
"""

import logging
from mcp_app import mcp
from utils.docker_client import get_docker_client, filter_containers
from utils.audit_logger import log_audit

logger = logging.getLogger(__name__)


@mcp.tool(
    name="check_containers_health",
    description="Check the health status of all Docker containers with health checks defined. Returns status with visual indicators (healthy, unhealthy, starting, or no health check)."
)
def check_containers_health():
    """
    Check health status of all containers with health checks defined
    
    Returns:
        str: Health status of containers
    """
    try:
        # Get Docker client
        client = get_docker_client()
        
        # List all containers
        containers = client.containers.list(all=True)
        
        # Filter containers
        containers = filter_containers(containers)
        
        # Log audit
        log_audit(operation="check_health", success=True, details={'count': len(containers)})
        
        if not containers:
            return "No containers found"
        
        # Check health status
        result = []
        healthy_count = 0
        unhealthy_count = 0
        no_health_check = 0
        
        for container in containers:
            health = container.attrs.get('State', {}).get('Health', {})
            status = health.get('Status', 'no health check')
            
            if status == 'healthy':
                status_symbol = "✅"
                healthy_count += 1
            elif status == 'unhealthy':
                status_symbol = "❌"
                unhealthy_count += 1
            elif status == 'starting':
                status_symbol = "🔄"
            else:
                status_symbol = "⚪"
                no_health_check += 1
            
            result.append(f"{status_symbol} {container.name}: {status} (state: {container.status})")
            
            # Add health check logs if unhealthy
            if status == 'unhealthy' and 'Log' in health:
                recent_log = health['Log'][-1] if health['Log'] else {}
                exit_code = recent_log.get('ExitCode', 'N/A')
                output = recent_log.get('Output', 'N/A')[:100]  # First 100 chars
                result.append(f"    Last check: ExitCode={exit_code}, Output={output}")
        
        summary = f"""Container Health Check Summary
=====================================
Total: {len(containers)}
Healthy: {healthy_count}
Unhealthy: {unhealthy_count}
No Health Check: {no_health_check}

Details:
{chr(10).join(result)}
"""
        
        return summary
        
    except Exception as e:
        logger.exception(f"Error checking container health: {e}")
        log_audit(operation="check_health", success=False, error=str(e))
        return f"Error checking container health: {str(e)}"
