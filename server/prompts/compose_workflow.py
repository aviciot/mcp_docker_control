"""
Docker Compose Workflow Prompt
================================
Guide for Docker Compose operations
"""

import logging
from mcp_app import mcp

logger = logging.getLogger(__name__)


@mcp.prompt()
def compose_workflow(project_name: str, compose_file_path: str = "./docker-compose.yml") -> str:
    """
    Docker Compose operations workflow.
    
    This prompt guides you through managing multi-container applications
    using Docker Compose commands with proper verification steps.
    
    Args:
        project_name: Name of the Docker Compose project
        compose_file_path: Path to docker-compose.yml file (default: ./docker-compose.yml)
    
    Returns:
        str: Docker Compose workflow instructions
    """
    
    return f"""# Docker Compose Workflow for Project: {project_name}

**Compose File:** {compose_file_path}

## Pre-Operation: Check Current State

### 1. List Current Services
Use `compose_status` tool with:
- compose_file="{compose_file_path}"
- project_name="{project_name}"

This shows:
- All services defined in compose file
- Current status (running/exited/created)
- Container names
- Port mappings

## Starting Services (compose up)

### 2. Start All Services
Use `compose_up` tool with:
- compose_file="{compose_file_path}"
- project_name="{project_name}"
- detached=true (run in background)
- build=false (use existing images)

**When to use:**
- Initial deployment
- After stopping all services
- Starting fresh environment

**Options:**
- build=true: Rebuild images before starting
- force_recreate=true: Recreate containers even if config unchanged
- pull=true: Pull latest images before starting

### 3. Verify Services Started
After compose up, wait 10-15 seconds then:

1. Check service status:
   Use `compose_status` tool again
   - All services should show "running"

2. Check individual container health:
   For each service, use `container_health` with container name
   - Verify health status = "healthy"

3. Review startup logs:
   Use `container_logs` for each service
   - Look for successful startup messages
   - Check for error messages

## Restarting Services

### 4. Restart All Services
Use `compose_restart` tool with:
- compose_file="{compose_file_path}"
- project_name="{project_name}"
- timeout=10 (seconds to wait before force restart)

**When to use:**
- After configuration changes
- When services become unresponsive
- After code updates (if volumes mounted)

**Note:** 
- Restart is faster than down + up
- Preserves volumes and networks
- Brief service interruption expected

### 5. Restart Specific Service
To restart just one service:
1. Get container name from `compose_status`
2. Use `restart_container` tool with that container name

## Stopping Services

### 6. Stop All Services (compose down)
Use `compose_down` tool with:
- compose_file="{compose_file_path}"
- project_name="{project_name}"
- remove_volumes=false (keep data)
- remove_orphans=true (clean up old containers)

**When to use:**
- Planned maintenance
- Major configuration changes
- Freeing up resources
- Before system reboot

**Options:**
- remove_volumes=true: **CAUTION** Deletes all data volumes
- timeout=10: Seconds to wait before force stop

### 7. Verify Services Stopped
After compose down:
Use `compose_status` tool
- All services should show "exited" or not present
- No containers should be running

## Updating Services

### 8. Update with New Images
**Workflow:**
1. Stop services: Use `compose_down`
2. Pull new images (done automatically with build=true)
3. Start services: Use `compose_up` with build=true
4. Verify each service health

### 9. Update Configuration
**Workflow:**
1. Modify docker-compose.yml file (outside MCP)
2. Restart services: Use `compose_restart`
   OR
3. Recreate: Use `compose_down` then `compose_up`
4. Verify configuration applied

## Troubleshooting Compose Issues

### Service Won't Start
1. Check logs: `container_logs` for the service container
2. Verify dependencies: Check if dependent services are running
3. Check ports: Look for port conflicts
4. Review compose file: Ensure configuration is valid

### Service Unhealthy After Start
1. Use `container_health` to check health status
2. Use `container_logs` to see recent errors
3. Use `container_stats` to check resource usage
4. May need to restart: Use `compose_restart`

### Can't Connect to Service
1. Check service is running: `compose_status`
2. Verify port mappings: Listed in compose status
3. Check network configuration in compose file
4. Test from within another container if possible

### High Resource Usage
1. Use `container_stats` on each service container
2. Identify heavy consumers
3. Use `troubleshoot_performance` prompt for analysis
4. Consider scaling or optimization

## Service Dependencies

### Understanding Service Order
**Networks:**
- Compose creates a default network
- All services can communicate by service name
- Example: service "web" can reach "db" at hostname "db"

**Depends_on:**
- Controls startup order
- Doesn't wait for service to be ready
- Use health checks for readiness

**Volumes:**
- Named volumes persist data
- Bind mounts link host directories
- Volume data survives compose down (unless remove_volumes=true)

## Best Practices

### 1. Regular Health Monitoring
**Daily:**
- Use `compose_status` to check all services
- Look for any exited or restarting services
- Investigate any issues immediately

### 2. Graceful Restarts
**Process:**
1. Check current status
2. Review recent logs for each service
3. Use `compose_restart` instead of down+up when possible
4. Verify health after restart
5. Check logs for errors

### 3. Safe Updates
**Process:**
1. Backup volumes/data (outside MCP)
2. Test in non-production first
3. Use `compose_down` (keep volumes)
4. Use `compose_up` with build=true
5. Verify each service individually
6. Monitor logs for 5-10 minutes

### 4. Resource Management
**Weekly:**
- Check resource usage: `container_stats` for each service
- Identify trends
- Plan capacity upgrades
- Optimize inefficient services

### 5. Clean Restarts
**Monthly or as needed:**
1. Backup critical data
2. `compose_down` with remove_orphans=true
3. Clean up old images (outside MCP)
4. `compose_up` with build=true
5. Fresh start with latest images

## Common Scenarios

### Scenario: One Service Failing
**Solution:**
1. Identify failing service: `compose_status`
2. Check its logs: `container_logs`
3. Restart just that service: `restart_container`
4. If still failing: `compose_restart` to restart all

### Scenario: After Code Changes
**Solution:**
1. If volumes mounted: `compose_restart`
2. If images need rebuild: `compose_down` then `compose_up` with build=true
3. Verify changes applied: Check logs

### Scenario: System Reboot
**Solution:**
1. After reboot: Services may not auto-start
2. Use `compose_up` to start all services
3. Verify health of each service
4. Check logs for any startup issues

### Scenario: Port Conflict
**Solution:**
1. Identify conflict: Check compose status and logs
2. Stop conflicting service (may be outside compose)
3. `compose_restart` to try again
4. Update port mapping in compose file if needed

## Safety Checks Before Operations

**Before compose_down:**
- ✅ Backup critical data
- ✅ Notify users of downtime
- ✅ Verify no critical operations in progress
- ✅ Check if volumes should be preserved

**Before compose_up:**
- ✅ Verify compose file is valid
- ✅ Check required images available
- ✅ Ensure sufficient resources
- ✅ Check no port conflicts

**Before compose_restart:**
- ✅ Check for active connections
- ✅ Verify no long-running operations
- ✅ Note current state for comparison
- ✅ Be ready to check logs immediately after
"""
