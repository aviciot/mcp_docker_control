"""
Diagnose Container Prompt
=========================
Comprehensive container diagnostics workflow
"""

import logging
from mcp_app import mcp

logger = logging.getLogger(__name__)


@mcp.prompt(
    name="diagnose_container",
    description="Comprehensive container diagnostic workflow including status checks, logs analysis, resource usage, and health verification."
)
def diagnose_container(container_name: str):
    """
    Comprehensive container diagnostic workflow.
    
    This prompt guides you through a complete diagnostic process for a Docker container,
    including status checks, logs analysis, resource usage, and health verification.
    
    Args:
        container_name: Name or ID of the container to diagnose
    
    Returns:
        str: Diagnostic workflow instructions
    """
    
    return f"""# Docker Container Diagnostic Workflow for: {container_name}

## Step 1: Check Container Status
Use `container_status` tool with container_name="{container_name}"
- Verify if container is running
- Check restart policy
- Review port mappings
- Note container state and health status

## Step 2: Retrieve Recent Logs
Use `container_logs` tool with:
- container_name="{container_name}"
- tail=50 (last 50 lines)
- timestamps=true
Look for:
- Error messages
- Warning patterns
- Startup failures
- Connection issues

## Step 3: Analyze Resource Usage
Use `container_stats` tool with container_name="{container_name}"
Check:
- CPU usage (high CPU might indicate inefficient code or runaway process)
- Memory usage (memory leaks, insufficient limits)
- Network I/O (bandwidth issues, connection problems)
- Disk I/O (slow disk, high write load)

## Step 4: Health Check Status
Use `container_health` tool with container_name="{container_name}"
Verify:
- Health check status (healthy/unhealthy/starting)
- Last health check output
- Number of failures

## Step 5: Analysis Summary
Based on the results above, provide:
1. Current status summary
2. Identified issues
3. Recommended actions
4. Whether restart/rebuild is needed

## Common Issues to Look For:
- Container stuck in restart loop → Check logs for startup errors
- High CPU/Memory → Resource limits too low or application issue
- Unhealthy status → Health check endpoint failing
- Port conflicts → Check port mappings and availability
- Volume mount issues → Check file permissions and paths

## Next Steps Based on Findings:
- If unhealthy but logs show no errors → Adjust health check configuration
- If high resource usage → Scale up resources or optimize application
- If restart loop → Fix configuration/environment issues, then restart
- If network issues → Check port mappings and firewall rules
"""
