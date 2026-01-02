"""
Docker Control MCP - Starlette Server
=====================================
Main server application with authentication middleware and auto-discovery
"""

import logging
import sys
from pathlib import Path
from contextlib import asynccontextmanager

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import PlainTextResponse, JSONResponse
from starlette.routing import Route
from starlette.requests import Request

from config import get_config, start_config_watcher, stop_config_watcher, validate_config
from utils.import_utils import auto_discover_modules
from utils.audit_logger import AuditLogger
from mcp_app import mcp

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
audit_logger = None


class AuthenticationMiddleware:
    """Middleware for password-based authentication"""
    
    def __init__(self, app, config: dict):
        self.app = app
        self.config = config
        self.auth_enabled = config.get('security', {}).get('authentication', {}).get('enabled', False)
        self.password = config.get('security', {}).get('authentication', {}).get('password', '')
        self.permission_level = config.get('security', {}).get('permissions', {}).get('level', 'full-control')
        
        # Define read-only tools (tools that don't modify state)
        self.read_only_tools = {
            'list_containers',
            'get_container_status',
            'get_container_logs',
            'get_container_stats',
            'check_containers_health',
            'compose_status'
        }
        
        # Define control tools (tools that modify state)
        self.control_tools = {
            'start_container',
            'stop_container',
            'restart_container',
            'compose_up',
            'compose_down',
            'compose_restart'
        }
        
        logger.info(f"Authentication middleware initialized (enabled={self.auth_enabled}, permission_level={self.permission_level})")
    
    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            await self.app(scope, receive, send)
            return
        
        # Skip auth for health check endpoints
        path = scope['path']
        if path in ['/healthz', '/health/deep']:
            await self.app(scope, receive, send)
            return
        
        # Check authentication if enabled
        if self.auth_enabled:
            headers = dict(scope['headers'])
            auth_header = headers.get(b'authorization', b'').decode('utf-8')
            
            # Support Bearer token format
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
            else:
                token = auth_header
            
            if token != self.password:
                # Return 401 Unauthorized
                response = JSONResponse(
                    {'error': 'Unauthorized', 'message': 'Invalid password'},
                    status_code=401
                )
                await response(scope, receive, send)
                return
        
        # Check permission level for control operations
        if self.permission_level == 'read-only':
            # Parse request to check if it's a control operation
            # We need to inspect the request body for MCP tool calls
            from starlette.requests import Request
            request = Request(scope, receive)
            
            try:
                body = await request.body()
                if body:
                    import json
                    data = json.loads(body)
                    
                    # Check if this is an MCP tool call
                    if data.get('method') == 'tools/call':
                        tool_name = data.get('params', {}).get('name', '')
                        
                        # Block control tools for read-only users
                        if tool_name in self.control_tools:
                            response = JSONResponse(
                                {
                                    'error': 'Forbidden',
                                    'message': f'Permission denied: {tool_name} requires full-control access. Current permission level: read-only'
                                },
                                status_code=403
                            )
                            
                            # Need to create a new receive callable with the body
                            async def receive_with_body():
                                return {'type': 'http.request', 'body': body}
                            
                            await response(scope, receive_with_body, send)
                            return
            except Exception as e:
                logger.error(f"Error checking permissions: {e}")
        
        # Authentication passed or not required
        await self.app(scope, receive, send)


async def healthz(request: Request):
    """Simple health check endpoint"""
    return PlainTextResponse("OK")


async def health_deep(request: Request):
    """Comprehensive health check with Docker connection"""
    from utils.docker_client import get_docker_client
    
    health = {
        'status': 'healthy',
        'checks': {}
    }
    
    try:
        # Check Docker connection
        client = get_docker_client()
        client.ping()
        health['checks']['docker'] = {'status': 'healthy', 'message': 'Docker daemon reachable'}
    except Exception as e:
        health['status'] = 'unhealthy'
        health['checks']['docker'] = {'status': 'unhealthy', 'message': str(e)}
    
    status_code = 200 if health['status'] == 'healthy' else 503
    return JSONResponse(health, status_code=status_code)


@asynccontextmanager
async def lifespan(app):
    """Lifecycle management for the application"""
    global audit_logger
    
    # Startup
    logger.info("=== Docker Control MCP Server Starting ===")
    
    # Load and validate configuration
    config = get_config()
    validate_config(config)
    logger.info(f"Configuration loaded: {config.get('mcp', {}).get('name')}")
    
    # Initialize audit logger
    audit_logger = AuditLogger(config)
    logger.info("Audit logger initialized")
    
    # Start configuration hot reload watcher
    if config.get('server', {}).get('hot_reload', True):
        start_config_watcher()
    
    # Auto-discover and load tools, resources, prompts
    if config.get('server', {}).get('auto_discover', True):
        logger.info("Auto-discovering modules...")
        auto_discover_modules()
    
    logger.info("=== Docker Control MCP Server Started ===")
    
    yield
    
    # Shutdown
    logger.info("=== Docker Control MCP Server Shutting Down ===")
    stop_config_watcher()
    if audit_logger:
        audit_logger.close()


# Load config for middleware
config = get_config()

# Create Starlette app with middleware
middleware = [
    Middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*']),
    Middleware(AuthenticationMiddleware, config=config)
]

routes = [
    Route('/healthz', healthz),
    Route('/health/deep', health_deep),
]

app = Starlette(
    routes=routes,
    middleware=middleware,
    lifespan=lifespan
)

# Mount FastMCP app (FastMCP 2.x uses __call__ directly)
app.mount('/', mcp)


if __name__ == "__main__":
    import uvicorn
    
    port = config.get('server', {}).get('port', 8300)
    host = config.get('server', {}).get('host', '0.0.0.0')
    
    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
