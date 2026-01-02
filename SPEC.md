# Docker Control MCP - Implementation Notes

**MCP Name:** docker-control-mcp  
**Purpose:** Docker container and Compose management with authentication and role-based permissions  
**Based On:** template_mcp patterns (January 2026)

---

## Implementation Details

This MCP was built following **template_mcp** patterns with these customizations:

### Custom Features
1. **Role-Based Permissions**
   - `read-only`: List, view status, logs, stats, health
   - `full-control`: All read-only + start, stop, restart, compose operations
   - Middleware enforces permission checks with 403 responses

2. **Container Filtering**
   - Whitelist/blacklist support via config
   - Pattern matching with wildcards
   - Configurable allowed/blocked containers

3. **Audit Logging**
   - JSON format to `logs/audit.log`
   - Records: operation, container, user, success/failure, errors
   - AuditLogger class accessible from all tools

4. **Docker Compose Support**
   - compose_up, compose_down, compose_restart, compose_status tools
   - Working directory management
   - Error handling for missing compose files

### Tools Implemented (12 total)
- `list_containers` - List all containers with filtering
- `container_status` - Detailed status with ports, state, health
- `container_logs` - Get logs with tail, since, timestamps
- `container_stats` - CPU, memory, network, disk I/O
- `container_health` - Health check with status symbols
- `start_container` - Start stopped container (requires full-control)
- `stop_container` - Stop running container (requires full-control)
- `restart_container` - Restart container (requires full-control)
- `compose_status` - List services in compose project
- `compose_up` - Start compose services (requires full-control)
- `compose_down` - Stop compose services (requires full-control)
- `compose_restart` - Restart compose services (requires full-control)

### Configuration Structure
```yaml
server:
  version: "1.0.0"
  host: "0.0.0.0"
  port: 8300
  hot_reload: true
  auto_discover: true

security:
  authentication:
    enabled: false  # Set AUTH_ENABLED=true in .env
    password: ""    # Set AUTH_PASSWORD in .env
  permissions:
    level: "full-control"  # Set AUTH_PERMISSION_LEVEL in .env

docker:
  socket: "/var/run/docker.sock"
  filter:
    mode: "allow_all"  # allow_all, allow_only, deny_only
    allowed_containers: []
    blocked_containers: []
  audit:
    enabled: true
    log_file: "logs/audit.log"
```

### Environment Variables
```bash
# .env file
AUTH_ENABLED=true               # Enable authentication
AUTH_PASSWORD=yourpassword      # Password for authentication
AUTH_PERMISSION_LEVEL=full-control  # read-only or full-control
MCP_PORT=8350                   # Port to run on
```

---

## Critical Patterns Followed

### ✅ Environment Variable Handling (Pattern #1)
Followed the **3-layer approach** correctly:
- YAML: Hardcoded defaults with comments
- Python: `os.getenv()` checks FIRST, then config fallback
- Docker Compose: Pass env vars explicitly

**server.py example:**
```python
auth_enabled = os.getenv('AUTH_ENABLED', '').lower() == 'true' if os.getenv('AUTH_ENABLED') else config.get('security', {}).get('authentication', {}).get('enabled', False)
password = os.getenv('AUTH_PASSWORD', '') or config.get('security', {}).get('authentication', {}).get('password', '')
port = int(os.getenv('MCP_PORT', config.get('server', {}).get('port', 8300)))
```

### ✅ FastMCP Mounting (Pattern #4)
Uses `mcp.http_app()` method correctly:
```python
mcp_http_app = mcp.http_app()
app.mount('/', mcp_http_app)
```

### ✅ Absolute Imports (Pattern #2)
All imports use absolute paths from server root:
```python
from config import get_config
from utils.docker_client import get_docker_client
from utils.audit_logger import audit_logger
```

### ✅ Auto-Discovery (Pattern #5)
All tools in `tools/` directory are auto-discovered on startup

### ✅ Package Management (Pattern #7)
Uses `uv` for fast package installation:
```dockerfile
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
RUN uv pip install --system --no-cache -r requirements.txt
```

---

## Deployment

### Build and Run
```bash
cd docker-control-mcp
docker-compose build
docker-compose up -d
```

### Health Check
```bash
curl -H "Authorization: yourpassword" http://localhost:8350/healthz
```

### Test Tool
```bash
# List containers (read-only permission OK)
curl -X POST http://localhost:8350/ \
  -H "Authorization: yourpassword" \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/call", "params": {"name": "list_containers"}}'
```

---

## Lessons Learned

### What Was Done Wrong Initially
1. **❌ Used `mcp._mcp_server` instead of `mcp.http_app()`**
   - Caused TypeError: 'LowLevelServer' object is not callable
   - Fixed by using public API method

2. **❌ Didn't check `os.getenv()` for environment variables**
   - Used `${}` expansion in YAML which doesn't work for booleans
   - AUTH_ENABLED=true in .env was ignored
   - Fixed by following template_mcp pattern with os.getenv() checks first

### What Worked Well
- ✅ Middleware for authentication and permission enforcement
- ✅ Audit logging integration with all tools
- ✅ Container filtering with whitelist/blacklist
- ✅ Hot-reload for config changes with watchdog
- ✅ Clean separation of concerns (tools, utils, config)

---

## Future Enhancements

- [ ] Add prompts for common Docker tasks
- [ ] Add resource for container metrics streaming
- [ ] Support Docker Swarm services
- [ ] Add volume management tools
- [ ] Add network management tools
- [ ] Add image management tools
- [ ] Support Docker contexts (remote Docker hosts)
- [ ] Add rate limiting per user
- [ ] Add WebSocket support for real-time logs

---

**Repository:** https://github.com/aviciot/mcp_docker_control  
**Last Updated:** January 2, 2026
