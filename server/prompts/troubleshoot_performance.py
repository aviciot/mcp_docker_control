"""
Troubleshoot Performance Prompt
================================
Analyze container performance issues
"""

import logging
from mcp_app import mcp

logger = logging.getLogger(__name__)


@mcp.prompt(
    name="troubleshoot_performance",
    description="Container performance troubleshooting workflow including resource analysis, optimization suggestions, and scaling recommendations."
)
def troubleshoot_performance(container_name: str):
    """
    Container performance troubleshooting workflow.
    
    This prompt guides you through analyzing container performance issues
    including resource usage, logs analysis, and optimization recommendations.
    
    Args:
        container_name: Name or ID of the container to analyze
    
    Returns:
        str: Performance troubleshooting workflow
    """
    
    return f"""# Container Performance Troubleshooting for: {container_name}

## Step 1: Current Resource Usage Analysis

### Check Real-Time Stats
Use `container_stats` tool with container_name="{container_name}"

Analyze the following metrics:

**CPU Usage:**
- Normal: < 50% average
- High: 50-80% sustained
- Critical: > 80% sustained
- Action: If high, check for inefficient code, infinite loops, or excessive calculations

**Memory Usage:**
- Check current vs limit
- Look for steady growth (potential memory leak)
- Sudden spikes indicate loading large datasets
- Action: If near limit, increase memory allocation or optimize application

**Network I/O:**
- RX (received): Inbound traffic
- TX (transmitted): Outbound traffic
- High values may indicate data transfer bottlenecks
- Action: Check network configuration, rate limiting, or API call frequency

**Block I/O:**
- Disk read/write operations
- High values indicate disk-intensive operations
- Action: Optimize database queries, add caching, or use faster storage

## Step 2: Log Pattern Analysis

### Review Recent Logs
Use `container_logs` tool with:
- container_name="{container_name}"
- tail=100
- timestamps=true

**Look for these patterns:**

1. **Error Patterns:**
   - Repeated error messages → Underlying issue needs fixing
   - Connection timeouts → Network/service availability issues
   - Out of memory errors → Increase memory limits

2. **Warning Patterns:**
   - Deprecation warnings → Future compatibility issues
   - Performance warnings → Application-level optimization needed
   - Resource warnings → Approaching limits

3. **Timing Patterns:**
   - Slow query logs → Database optimization needed
   - Long response times → Performance bottleneck
   - Timeout warnings → Increase timeout thresholds

## Step 3: Health Check Analysis

Use `container_health` tool with container_name="{container_name}"

Check:
- Is health check failing? → Application not responding correctly
- Health check response time → Slow response indicates performance issue
- Failure count → Intermittent issues if count > 0

## Step 4: Container Configuration Review

Use `container_status` tool to check:

**Resource Limits:**
- Are memory/CPU limits set too low?
- Is container hitting limits (throttling)?
- Compare usage to limits

**Restart Policy:**
- Restart count > 5 indicates instability
- Recent restarts may explain temporary performance issues

**Port Mappings:**
- Verify correct ports exposed
- Check for port conflicts

## Common Performance Issues & Solutions

### High CPU Usage:
**Causes:**
- Infinite loops or inefficient algorithms
- Too many concurrent requests
- CPU-intensive operations (encryption, compression)
- Insufficient caching

**Solutions:**
- Profile application code
- Implement request throttling
- Add caching layers
- Scale horizontally (add more containers)

### High Memory Usage:
**Causes:**
- Memory leaks
- Large in-memory caches
- Loading entire datasets into memory
- Insufficient garbage collection

**Solutions:**
- Fix memory leaks in code
- Implement memory limits and monitoring
- Use streaming for large datasets
- Tune garbage collection settings

### High Disk I/O:
**Causes:**
- Excessive logging
- Database operations without indexes
- File processing without buffering
- Temporary file creation

**Solutions:**
- Reduce log verbosity
- Optimize database queries
- Use buffered I/O
- Clean up temporary files

### Network Issues:
**Causes:**
- Slow external API calls
- Database connection issues
- Large payload transfers
- Network congestion

**Solutions:**
- Implement connection pooling
- Add timeout configurations
- Compress payloads
- Use CDN for static content

## Step 5: Optimization Recommendations

Based on findings, suggest:

1. **Immediate Actions:**
   - Increase resource limits if near capacity
   - Fix critical errors in logs
   - Restart if memory leak suspected

2. **Short-term:**
   - Add monitoring alerts
   - Implement caching
   - Optimize slow queries

3. **Long-term:**
   - Code profiling and optimization
   - Architecture improvements
   - Horizontal scaling strategy

## Monitoring Best Practices:
- Set up alerts for CPU > 80%, Memory > 90%
- Monitor restart count
- Track response time trends
- Log aggregation for pattern analysis
"""
