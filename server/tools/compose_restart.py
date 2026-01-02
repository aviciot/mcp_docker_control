"""
Docker Compose Restart Tool
===========================
Restart Docker Compose services
"""

import logging
import subprocess
from pathlib import Path
from mcp_app import mcp
from utils.audit_logger import log_audit

logger = logging.getLogger(__name__)


@mcp.tool(
    name="compose_restart",
    description="Restart Docker Compose services gracefully with configurable timeout. Requires full-control permission level."
)
def compose_restart(project_path: str, services: str = ""):
    """
    Restart Docker Compose services
    
    Args:
        project_path: Path to directory containing docker-compose.yml
        services: Space-separated list of service names to restart (empty = all services)
    
    Returns:
        str: Success or error message
    """
    try:
        # Validate input
        if not project_path:
            return "Error: project_path cannot be empty"
        
        # Validate path exists
        path = Path(project_path)
        if not path.exists():
            log_audit(operation="compose_restart", success=False, error=f"Path not found: {project_path}")
            return f"Error: Path not found: {project_path}"
        
        # Check for compose file
        compose_file = path / "docker-compose.yml"
        if not compose_file.exists():
            compose_file = path / "docker-compose.yaml"
            if not compose_file.exists():
                log_audit(operation="compose_restart", success=False, error="docker-compose.yml not found")
                return f"Error: docker-compose.yml not found in {project_path}"
        
        # Build command
        cmd = ['docker-compose', 'restart']
        if services:
            cmd.extend(services.split())
        
        # Run docker-compose restart
        result = subprocess.run(
            cmd,
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=120  # 2 minutes
        )
        
        success = result.returncode == 0
        
        # Log audit
        log_audit(
            operation="compose_restart",
            success=success,
            details={'project_path': project_path, 'services': services or 'all'},
            error=None if success else result.stderr
        )
        
        if success:
            return f"Successfully restarted Docker Compose services in {project_path}\n\n{result.stdout}"
        else:
            return f"Error restarting Docker Compose services:\n{result.stderr}"
        
    except subprocess.TimeoutExpired:
        logger.error("docker-compose restart command timed out")
        log_audit(operation="compose_restart", success=False, error="Command timeout")
        return "Error: docker-compose restart command timed out (exceeded 2 minutes)"
    except FileNotFoundError:
        logger.error("docker-compose command not found")
        log_audit(operation="compose_restart", success=False, error="docker-compose not installed")
        return "Error: docker-compose command not found. Is Docker Compose installed?"
    except Exception as e:
        logger.exception(f"Error running compose restart: {e}")
        log_audit(operation="compose_restart", success=False, error=str(e))
        return f"Error running compose restart: {str(e)}"
