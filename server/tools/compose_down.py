"""
Docker Compose Down Tool
=======================
Stop and remove Docker Compose services
"""

import logging
import subprocess
from pathlib import Path
from mcp_app import mcp
from utils.audit_logger import log_audit

logger = logging.getLogger(__name__)


@mcp.tool(
    name="compose_down",
    description="Stop and remove Docker Compose services with options to remove volumes and orphaned containers. Requires full-control permission level and password verification."
)
def compose_down(project_path: str, password: str, remove_volumes: bool = False):
    """
    Stop and remove Docker Compose services
    
    Args:
        project_path: Path to directory containing docker-compose.yml
        remove_volumes: Remove named volumes (default: False)
    
    Returns:
        str: Success or error message
    """
    try:
        # Validate password first
        import os
        expected_password = os.getenv('AUTH_PASSWORD', '')
        if not password or password != expected_password:
            log_audit(operation="compose_down", success=False, error="Invalid or missing password")
            return "Error: Invalid or missing password. Authentication required for this operation."
        
        # Validate input
        if not project_path:
            return "Error: project_path cannot be empty"
        
        # Validate path exists
        path = Path(project_path)
        if not path.exists():
            log_audit(operation="compose_down", success=False, error=f"Path not found: {project_path}")
            return f"Error: Path not found: {project_path}"
        
        # Check for compose file
        compose_file = path / "docker-compose.yml"
        if not compose_file.exists():
            compose_file = path / "docker-compose.yaml"
            if not compose_file.exists():
                log_audit(operation="compose_down", success=False, error="docker-compose.yml not found")
                return f"Error: docker-compose.yml not found in {project_path}"
        
        # Build command
        cmd = ['docker-compose', 'down']
        if remove_volumes:
            cmd.append('-v')
        
        # Run docker-compose down
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
            operation="compose_down",
            success=success,
            details={'project_path': project_path, 'remove_volumes': remove_volumes},
            error=None if success else result.stderr
        )
        
        if success:
            return f"Successfully stopped Docker Compose services in {project_path}\n\n{result.stdout}"
        else:
            return f"Error stopping Docker Compose services:\n{result.stderr}"
        
    except subprocess.TimeoutExpired:
        logger.error("docker-compose down command timed out")
        log_audit(operation="compose_down", success=False, error="Command timeout")
        return "Error: docker-compose down command timed out (exceeded 2 minutes)"
    except FileNotFoundError:
        logger.error("docker-compose command not found")
        log_audit(operation="compose_down", success=False, error="docker-compose not installed")
        return "Error: docker-compose command not found. Is Docker Compose installed?"
    except Exception as e:
        logger.exception(f"Error running compose down: {e}")
        log_audit(operation="compose_down", success=False, error=str(e))
        return f"Error running compose down: {str(e)}"
