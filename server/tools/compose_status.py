"""
Docker Compose Status Tool
==========================
Get status of Docker Compose services
"""

import logging
import subprocess
from pathlib import Path
from mcp_app import mcp
from utils.audit_logger import log_audit
from config import get_config

logger = logging.getLogger(__name__)


@mcp.tool()
async def compose_status(project_path: str) -> str:
    """
    Get status of Docker Compose services
    
    Args:
        project_path: Path to directory containing docker-compose.yml
    
    Returns:
        str: Status of compose services
    """
    try:
        # Validate input
        if not project_path:
            return "Error: project_path cannot be empty"
        
        # Validate path exists
        path = Path(project_path)
        if not path.exists():
            log_audit(operation="compose_status", success=False, error=f"Path not found: {project_path}")
            return f"Error: Path not found: {project_path}"
        
        # Check for compose file
        compose_file = path / "docker-compose.yml"
        if not compose_file.exists():
            compose_file = path / "docker-compose.yaml"
            if not compose_file.exists():
                log_audit(operation="compose_status", success=False, error="docker-compose.yml not found")
                return f"Error: docker-compose.yml not found in {project_path}"
        
        # Run docker-compose ps
        result = subprocess.run(
            ['docker-compose', 'ps'],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Log audit
        log_audit(
            operation="compose_status",
            success=True,
            details={'project_path': project_path}
        )
        
        output = result.stdout if result.stdout else "No services found"
        return f"Docker Compose Status ({project_path}):\n{'=' * 50}\n{output}"
        
    except subprocess.TimeoutExpired:
        logger.error("docker-compose ps command timed out")
        log_audit(operation="compose_status", success=False, error="Command timeout")
        return "Error: docker-compose ps command timed out"
    except FileNotFoundError:
        logger.error("docker-compose command not found")
        log_audit(operation="compose_status", success=False, error="docker-compose not installed")
        return "Error: docker-compose command not found. Is Docker Compose installed?"
    except Exception as e:
        logger.exception(f"Error getting compose status: {e}")
        log_audit(operation="compose_status", success=False, error=str(e))
        return f"Error getting compose status: {str(e)}"
