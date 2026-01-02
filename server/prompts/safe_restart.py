"""
Safe Restart Prompt
===================
Safely restart a container with pre/post checks
"""

import logging
from mcp_app import mcp

logger = logging.getLogger(__name__)


@mcp.prompt()
def safe_restart(container_name: str) -> str:
    """
    Safe container restart workflow with verification.
    
    This prompt guides you through a safe restart process that verifies
    container state before and after restart to ensure successful recovery.
    
    Args:
        container_name: Name or ID of the container to restart
    
    Returns:
        str: Safe restart workflow instructions
    """
    
    return f"""# Safe Container Restart Workflow for: {container_name}

## Pre-Restart Checks

### 1. Verify Container Exists and Current State
Use `container_status` tool with container_name="{container_name}"
- Confirm container exists
- Note current state (running/stopped/paused)
- Record current health status
- Save port mappings for verification

### 2. Check for Active Connections (if applicable)
Use `container_logs` tool with tail=20 to see recent activity
- Look for active connections
- Check for in-progress operations
- Note any warnings about pending work

### 3. Backup Critical Information
Before restart, document:
- Current uptime
- Recent error patterns in logs
- Resource usage baseline
- Health check status

## Execute Restart

### 4. Perform Container Restart
Use `restart_container` tool with container_name="{container_name}"
- This will gracefully stop and start the container
- Container will attempt to restart with same configuration
- Wait 10-15 seconds for startup

## Post-Restart Verification

### 5. Verify Container Started Successfully
Use `container_status` tool again:
- Confirm state is "running"
- Verify ports are mapped correctly
- Check restart count increased by 1

### 6. Monitor Startup Logs
Use `container_logs` tool with:
- tail=30
- timestamps=true
Look for:
- Successful startup messages
- No immediate errors
- Application initialization complete

### 7. Verify Health Status
Use `container_health` tool:
- Wait 30 seconds for health checks to run
- Confirm status is "healthy" or "starting"
- If unhealthy, check logs immediately

### 8. Quick Performance Check
Use `container_stats` tool:
- Verify CPU/Memory usage is normal
- Check for immediate resource spikes
- Confirm network connectivity

## Success Criteria:
✅ Container state = running
✅ Health status = healthy (or starting)
✅ No errors in recent logs
✅ Ports correctly mapped
✅ Resource usage within normal range

## If Restart Fails:
1. Check logs for error messages
2. Verify configuration hasn't changed
3. Check Docker daemon status
4. Review available resources (CPU, memory, disk)
5. Consider `docker compose restart` if part of a stack
6. Last resort: stop + start instead of restart

## Notes:
- Restart preserves container configuration
- Volumes and networks remain intact
- Restart count increments
- Brief downtime expected (typically 5-10 seconds)
"""
