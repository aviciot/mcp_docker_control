"""
List By Status Prompt
=====================
Filter and list containers by various criteria
"""

import logging
from mcp_app import mcp

logger = logging.getLogger(__name__)


@mcp.prompt()
def list_by_status() -> str:
    """
    Guide for filtering and listing containers by status and other criteria.
    
    This prompt provides instructions on how to effectively use the list_containers
    tool with various filters to find specific containers.
    
    Returns:
        str: Container listing and filtering instructions
    """
    
    return """# Docker Container Filtering and Listing Guide

## Basic Listing

### List All Containers
Use `list_containers` tool with:
- all=true (includes stopped containers)
- all=false (only running containers)

## Filter by Status

### Running Containers Only
Use `list_containers` with filters={"status": ["running"]}
- Shows actively running containers
- Useful for checking current workload

### Stopped Containers Only
Use `list_containers` with filters={"status": ["exited"]}
- Shows containers that have stopped
- Helpful for cleanup or restart identification

### Paused Containers
Use `list_containers` with filters={"status": ["paused"]}
- Shows containers temporarily paused
- Rare but useful for troubleshooting

### Created but Not Started
Use `list_containers` with filters={"status": ["created"]}
- Containers created but never started
- May indicate deployment issues

### Restarting Containers (Problematic)
Use `list_containers` with filters={"status": ["restarting"]}
- Containers stuck in restart loop
- **High priority for investigation!**
- Often indicates configuration or application errors

## Filter by Health Status

### Healthy Containers
Use `list_containers` with filters={"health": ["healthy"]}
- All health checks passing
- Normal operation

### Unhealthy Containers (Action Required!)
Use `list_containers` with filters={"health": ["unhealthy"]}
- **Critical: Immediate attention needed**
- Health checks failing
- Use `diagnose_container` prompt for each unhealthy container

### Starting Containers
Use `list_containers` with filters={"health": ["starting"]}
- Health checks not yet complete
- Wait 30-60 seconds then re-check

### No Health Check Configured
Use `list_containers` with filters={"health": ["none"]}
- Containers without health checks
- Consider adding health checks for monitoring

## Filter by Name Pattern

### Find Specific Container
Use `list_containers` with filters={"name": ["container_name"]}
- Exact or partial name match
- Case-sensitive

### Find by Prefix
Use `list_containers` with filters={"name": ["^/prefix"]}
- All containers starting with "prefix"
- Useful for grouped services (e.g., "app-*", "db-*")

## Filter by Image

### Find Containers from Specific Image
Use `list_containers` with filters={"ancestor": ["image:tag"]}
- All containers created from specific image
- Useful for version tracking

### Find Containers with Tag Pattern
Use `list_containers` with filters={"ancestor": ["image:*"]}
- All versions of an image
- Helpful for multi-version deployments

## Filter by Label

### Find Containers with Specific Label
Use `list_containers` with filters={"label": ["key=value"]}
- Containers with matching label
- Useful for environment separation (e.g., label=env=production)

### Find Containers with Label Key Only
Use `list_containers` with filters={"label": ["key"]}
- Containers having the label regardless of value
- Good for categorization

## Common Use Cases

### Find Problem Containers
**Goal:** Identify containers needing attention

1. List unhealthy containers:
   filters={"health": ["unhealthy"]}

2. List restarting containers:
   filters={"status": ["restarting"]}

3. For each problem container, use `diagnose_container` prompt

### Environment Inventory
**Goal:** See what's running in production

1. List all running containers:
   filters={"status": ["running"]}

2. For each container, note:
   - Name and image version
   - Resource usage (use `container_stats`)
   - Health status (use `container_health`)

### Cleanup Candidates
**Goal:** Find stopped containers to remove

1. List exited containers:
   filters={"status": ["exited"]}

2. Review each container's purpose
3. Consider removing unnecessary stopped containers

### Performance Audit
**Goal:** Find resource-intensive containers

1. List all running containers
2. For each container:
   - Use `container_stats` to check CPU/memory
   - Identify high consumers
   - Use `troubleshoot_performance` prompt for analysis

### Deployment Verification
**Goal:** Confirm new version deployed

1. List containers from new image:
   filters={"ancestor": ["image:new-tag"]}

2. Verify all expected containers running
3. Check health status for each
4. Review logs for startup errors

## Combining Filters

### Multiple Status Filters
filters={"status": ["running", "restarting"]}
- Running OR restarting containers

### Multiple Criteria
filters={
  "status": ["running"],
  "health": ["unhealthy"]
}
- Running AND unhealthy (highest priority!)

## Output Information

Each container listing includes:
- **Name**: Container identifier
- **Status**: Current state (running/exited/etc.)
- **Image**: Source image and tag
- **Ports**: Exposed port mappings
- **Created**: When container was created
- **Health**: Health check status (if configured)

## Best Practices

1. **Regular Health Checks:**
   - Run weekly: filters={"health": ["unhealthy"]}
   - Investigate and fix all unhealthy containers

2. **Monitor Restart Loops:**
   - Check daily: filters={"status": ["restarting"]}
   - These indicate serious issues

3. **Cleanup Stopped Containers:**
   - Monthly review: filters={"status": ["exited"]}
   - Remove unnecessary containers

4. **Track Resource Usage:**
   - List all running containers
   - Use `container_stats` for top consumers
   - Plan capacity accordingly

5. **Version Tracking:**
   - List by image ancestor
   - Ensure correct versions deployed
   - Plan upgrade strategy
"""
