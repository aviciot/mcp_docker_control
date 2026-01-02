"""
Docker Compose Up Tool
=====================
Start Docker Compose services
"""

import logging
import subprocess
from pathlib import Path
from mcp_app import mcp
from utils.audit_logger import log_audit

logger = logging.getLogger(__name__)


@mcp.tool()
async def compose_up(project_path: str, detached: bool = True, build: bool = False) -> str:
    """
    Start Docker Compose services
    
    Args:
        project_path: Path to directory containing docker-compose.yml
        detached: Run in detached mode (default: True)
        build: Build images before starting (default: False)
    
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
            log_audit(operation="compose_up", success=False, error=f"Path not found: {project_path}")
            return f"Error: Path not found: {project_path}"
        
        # Check for compose file
        compose_file = path / "docker-compose.yml"
        if not compose_file.exists():
            compose_file = path / "docker-compose.yaml"
            if not compose_file.exists():
                log_audit(operation="compose_up", success=False, error="docker-compose.yml not found")
                return f"Error: docker-compose.yml not found in {project_path}"
        
        # Build command
        cmd = ['docker-compose', 'up']
        if detached:
            cmd.append('-d')
        if build:
            cmd.append('--build')
        
        # Run docker-compose up
        result = subprocess.run(
            cmd,
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes for building
        )
        
        success = result.returncode == 0
        
        # Log audit
        log_audit(
            operation="compose_up",
            success=success,
            details={'project_path': project_path, 'detached': detached, 'build': build},
            error=None if success else result.stderr
        )
        
        if success:
            return f"Successfully started Docker Compose services in {project_path}\n\n{result.stdout}"
        else:
            return f"Error starting Docker Compose services:\n{result.stderr}"
        
    except subprocess.TimeoutExpired:
        logger.error("docker-compose up command timed out")
        log_audit(operation="compose_up", success=False, error="Command timeout")
        return "Error: docker-compose up command timed out (exceeded 5 minutes)"
    except FileNotFoundError:
        logger.error("docker-compose command not found")
        log_audit(operation="compose_up", success=False, error="docker-compose not installed")
        return "Error: docker-compose command not found. Is Docker Compose installed?"
    except Exception as e:
        logger.exception(f"Error running compose up: {e}")
        log_audit(operation="compose_up", success=False, error=str(e))
        return f"Error running compose up: {str(e)}"
