# Docker Control MCP

**Docker Control MCP** is a Model Context Protocol (MCP) server that enables AI assistants (like Claude) to manage Docker containers and Docker Compose services with password-protected operations, whitelist/blacklist filtering, audit logging, and hot-reloadable configuration.

## Features

### 🐳 Container Management
- **List containers** - View all running or stopped containers
- **Get container status** - Detailed status, state, ports, and health information
- **Get container logs** - Retrieve logs with filtering (tail, since, timestamps)
- **Container stats** - Real-time CPU, memory, network, and disk I/O statistics
- **Health checks** - Monitor container health status across all containers

### 🎛️ Container Control
- **Start containers** - Start stopped containers
- **Stop containers** - Gracefully stop running containers
- **Restart containers** - Restart containers with configurable timeout

### 📦 Docker Compose Support
- **Compose status** - View status of all services in a project
- **Compose up** - Start services with optional build
- **Compose down** - Stop and remove services
- **Compose restart** - Restart specific or all services

### 🔒 Security Features
- **Password authentication** - Optional Bearer token authentication
- **Whitelist/Blacklist filtering** - Restrict container access
- **Audit logging** - Complete audit trail of all operations
- **Read-only Docker socket** - Mount Docker socket as read-only for safety

### ⚙️ Configuration
- **YAML-based configuration** - Easy-to-edit settings
- **Hot reload** - Configuration changes applied without restart
- **Environment-specific configs** - Separate settings for dev/prod
- **Environment variable expansion** - Support ${VAR:-default} syntax

## Quick Start

### 1. Installation

```bash
cd docker-control-mcp
pip install -r server/requirements.txt
```

### 2. Configuration

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` to configure:
```env
MCP_PORT=8300
ENV=default  # or dev, prod
AUTH_ENABLED=false
AUTH_PASSWORD=your-secure-password
```

Edit `server/config/settings.yaml` to configure filtering:
```yaml
docker:
  filter:
    # Whitelist: Only these containers (empty = all allowed)
    whitelist: []
    
    # Blacklist: Exclude these containers
    blacklist: []
```

### 3. Running Locally

```bash
cd server
python server.py
```

Server will start on `http://localhost:8300`

### 4. Running with Docker

```bash
docker-compose up -d
```

### 5. Testing

Run the comprehensive test suite:
```bash
python test_script.py
```

Run pytest unit tests:
```bash
pip install -r tests/requirements.txt
pytest tests/ -v
```

## Configuration

### Settings Files

- **settings.yaml** - Base configuration
- **settings.dev.yaml** - Development overrides (use `ENV=dev`)
- **settings.prod.yaml** - Production overrides (use `ENV=prod`)

### Configuration Structure

```yaml
server:
  port: 8300
  host: "0.0.0.0"
  hot_reload: true
  auto_discover: true

mcp:
  name: "docker-control"

security:
  authentication:
    enabled: false
    password: ""

docker:
  socket_path: "/var/run/docker.sock"
  filter:
    whitelist: []  # Only these containers
    blacklist: []  # Exclude these containers
  audit:
    enabled: true
    log_path: "logs/audit.log"
```

### Filtering Examples

**Whitelist only specific containers:**
```yaml
docker:
  filter:
    whitelist: ["app-container", "db-container", "redis-container"]
    blacklist: []
```

**Blacklist sensitive containers:**
```yaml
docker:
  filter:
    whitelist: []
    blacklist: ["production-db", "payment-service"]
```

## API Endpoints

### Health Checks

- `GET /healthz` - Simple health check
- `GET /health/deep` - Comprehensive health check with Docker connection

### MCP Tools

All tools are accessed via the MCP protocol at `/mcp`.

#### Read-Only Tools

- `list_containers(all_containers: bool = False)` - List containers
- `get_container_status(container_name: str)` - Get container status
- `get_container_logs(container_name: str, tail: int = 100, since: str = "", timestamps: bool = False)` - Get logs
- `get_container_stats(container_name: str)` - Get resource statistics
- `check_containers_health()` - Check health of all containers

#### Control Tools

- `start_container(container_name: str)` - Start a container
- `stop_container(container_name: str, timeout: int = 10)` - Stop a container
- `restart_container(container_name: str, timeout: int = 10)` - Restart a container

#### Compose Tools

- `compose_status(project_path: str)` - Get Compose service status
- `compose_up(project_path: str, detached: bool = True, build: bool = False)` - Start services
- `compose_down(project_path: str, remove_volumes: bool = False)` - Stop services
- `compose_restart(project_path: str, services: str = "")` - Restart services

## Authentication

When authentication is enabled (`AUTH_ENABLED=true`), all requests (except `/healthz` and `/health/deep`) require a Bearer token:

```bash
Authorization: Bearer your-password-here
```

Example with curl:
```bash
curl -H "Authorization: Bearer your-password" \
     http://localhost:8300/mcp
```

## Audit Logging

All Docker operations are logged to `logs/audit.log` in JSON format:

```json
{
  "timestamp": "2026-01-02T10:00:00.000000",
  "operation": "start",
  "container": "app-container",
  "user": "system",
  "success": true,
  "details": {}
}
```

## Architecture

### Project Structure

```
docker-control-mcp/
├── server/
│   ├── config.py              # Configuration loader with hot reload
│   ├── server.py              # Starlette app with auth middleware
│   ├── mcp_app.py             # FastMCP instance
│   │
│   ├── config/                # Configuration files
│   │   ├── settings.yaml
│   │   ├── settings.dev.yaml
│   │   └── settings.prod.yaml
│   │
│   ├── tools/                 # MCP Tools (auto-discovered)
│   │   ├── list_containers.py
│   │   ├── container_status.py
│   │   ├── container_logs.py
│   │   ├── start_container.py
│   │   ├── stop_container.py
│   │   ├── restart_container.py
│   │   ├── container_stats.py
│   │   ├── container_health.py
│   │   ├── compose_status.py
│   │   ├── compose_up.py
│   │   ├── compose_down.py
│   │   └── compose_restart.py
│   │
│   └── utils/                 # Utility modules
│       ├── import_utils.py    # Auto-discovery
│       ├── audit_logger.py    # Audit logging
│       └── docker_client.py   # Docker client wrapper
│
├── tests/                     # Unit tests
├── test_script.py             # End-to-end test script
├── docker-compose.yml
└── README.md
```

### Following SPEC.md Patterns

This MCP follows the patterns defined in [template_mcp/SPEC.md](../template_mcp/SPEC.md):

- ✅ Absolute imports only (no relative imports)
- ✅ `config.py` as module (not package)
- ✅ FastMCP 2.x API (`mcp = FastMCP(name="docker-control")`)
- ✅ Minimal `mcp_app.py` (only FastMCP instance)
- ✅ Auto-discovery of tools
- ✅ Error handling in all tools
- ✅ Input validation
- ✅ Authentication middleware in `server.py`
- ✅ Health check endpoints

## Use Cases

### Use Case 1: Monitor Container Health

```python
# Check health of all containers
check_containers_health()

# Get detailed status of a specific container
get_container_status("app-container")

# Get resource usage
get_container_stats("app-container")
```

### Use Case 2: Restart Unhealthy Container

```python
# Check status
status = get_container_status("app-container")

# If unhealthy, restart
if "unhealthy" in status:
    restart_container("app-container")
```

### Use Case 3: Manage Docker Compose Project

```python
# Check status
compose_status("/path/to/project")

# Restart services
compose_restart("/path/to/project", services="web api")

# Full rebuild
compose_down("/path/to/project")
compose_up("/path/to/project", build=True)
```

### Use Case 4: Investigate Issues

```python
# Get recent logs
get_container_logs("app-container", tail=100, timestamps=True)

# Get logs since a specific time
get_container_logs("app-container", since="1h")

# Check resource usage
get_container_stats("app-container")
```

## Security Considerations

1. **Docker Socket Access** - The MCP requires access to the Docker socket. In production, mount it as read-only when possible.

2. **Authentication** - Always enable authentication in production:
   ```yaml
   security:
     authentication:
       enabled: true
       password: "strong-random-password-here"
   ```

3. **Filtering** - Use whitelist/blacklist to restrict container access:
   ```yaml
   docker:
     filter:
       whitelist: ["allowed-container-1", "allowed-container-2"]
   ```

4. **Audit Logging** - Review audit logs regularly for suspicious activity.

5. **Network Isolation** - Run the MCP in a private network or behind a firewall.

## Troubleshooting

### Cannot connect to Docker daemon

**Error**: `Cannot connect to Docker daemon at unix:///var/run/docker.sock`

**Solution**: 
- Ensure Docker is running
- Check Docker socket path in configuration
- Verify user has permission to access Docker socket

### Authentication fails

**Error**: `401 Unauthorized`

**Solution**:
- Check `AUTH_ENABLED` is set correctly
- Verify password matches `AUTH_PASSWORD`
- Ensure Bearer token is sent in Authorization header

### Container not allowed

**Error**: `Container not allowed by filter: container-name`

**Solution**:
- Check whitelist/blacklist configuration
- Add container to whitelist or remove from blacklist

### Hot reload not working

**Solution**:
- Check `hot_reload: true` in configuration
- Ensure `watchdog` package is installed
- Check file system events are supported

## Development

### Adding New Tools

1. Create a new file in `server/tools/` (e.g., `my_tool.py`)
2. Import `mcp` from `mcp_app`
3. Define tool with `@mcp.tool()` decorator
4. Tool will be auto-discovered on server start

Example:
```python
from mcp_app import mcp
from utils.audit_logger import log_audit

@mcp.tool()
async def my_tool(param: str) -> str:
    """Tool description"""
    try:
        # Validate input
        if not param:
            return "Error: param cannot be empty"
        
        # Execute logic
        result = f"Processed: {param}"
        
        # Log audit
        log_audit("my_tool", success=True)
        
        return result
    except Exception as e:
        log_audit("my_tool", success=False, error=str(e))
        return f"Error: {str(e)}"
```

### Running Tests

```bash
# Run end-to-end tests
python test_script.py

# Run unit tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=server --cov-report=html
```

## License

MIT License - see LICENSE file for details

## Contributing

Contributions welcome! Please:
1. Follow the SPEC.md patterns
2. Add tests for new features
3. Update documentation
4. Ensure audit logging for sensitive operations

## Support

For issues or questions:
- Check troubleshooting section
- Review SPEC.md for implementation patterns
- Check audit logs for operation details
