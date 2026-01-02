"""
Docker Client Wrapper
=====================
Wrapper around Docker SDK with filtering, whitelist/blacklist support
"""

import logging
import docker
from typing import List, Dict, Any, Optional
from docker.models.containers import Container

from config import get_config

logger = logging.getLogger(__name__)

# Global Docker client instance
_docker_client: Optional[docker.DockerClient] = None


def get_docker_client() -> docker.DockerClient:
    """Get or create Docker client instance"""
    global _docker_client
    
    if _docker_client is None:
        config = get_config()
        socket_path = config.get('docker', {}).get('socket_path', '/var/run/docker.sock')
        
        try:
            _docker_client = docker.DockerClient(base_url=f'unix://{socket_path}')
            logger.info(f"Docker client connected: {socket_path}")
        except Exception as e:
            logger.error(f"Failed to connect to Docker: {e}")
            raise
    
    return _docker_client


def is_container_allowed(container_name: str) -> bool:
    """
    Check if a container is allowed based on whitelist/blacklist
    
    Args:
        container_name: Container name or ID
    
    Returns:
        True if container is allowed, False otherwise
    """
    config = get_config()
    
    # Get whitelist and blacklist
    whitelist = config.get('docker', {}).get('filter', {}).get('whitelist', [])
    blacklist = config.get('docker', {}).get('filter', {}).get('blacklist', [])
    
    # If whitelist exists, container must be in whitelist
    if whitelist:
        return container_name in whitelist
    
    # If blacklist exists, container must not be in blacklist
    if blacklist:
        return container_name not in blacklist
    
    # No filtering - allow all
    return True


def filter_containers(containers: List[Container]) -> List[Container]:
    """
    Filter containers based on whitelist/blacklist
    
    Args:
        containers: List of Docker containers
    
    Returns:
        Filtered list of containers
    """
    config = get_config()
    
    # Get whitelist and blacklist
    whitelist = config.get('docker', {}).get('filter', {}).get('whitelist', [])
    blacklist = config.get('docker', {}).get('filter', {}).get('blacklist', [])
    
    # No filtering - return all
    if not whitelist and not blacklist:
        return containers
    
    filtered = []
    for container in containers:
        container_name = container.name
        
        # Check whitelist
        if whitelist:
            if container_name in whitelist:
                filtered.append(container)
            continue
        
        # Check blacklist
        if blacklist:
            if container_name not in blacklist:
                filtered.append(container)
            continue
        
        filtered.append(container)
    
    return filtered


def get_container_by_name_or_id(name_or_id: str) -> Optional[Container]:
    """
    Get container by name or ID
    
    Args:
        name_or_id: Container name or ID
    
    Returns:
        Container object or None if not found
    
    Raises:
        PermissionError: If container is not allowed by filter
    """
    # Check if container is allowed
    if not is_container_allowed(name_or_id):
        raise PermissionError(f"Container not allowed by filter: {name_or_id}")
    
    client = get_docker_client()
    
    try:
        container = client.containers.get(name_or_id)
        return container
    except docker.errors.NotFound:
        return None
    except Exception as e:
        logger.error(f"Error getting container {name_or_id}: {e}")
        raise


def format_container_info(container: Container) -> Dict[str, Any]:
    """
    Format container information for display
    
    Args:
        container: Docker container object
    
    Returns:
        Dictionary with formatted container information
    """
    return {
        'id': container.short_id,
        'name': container.name,
        'image': container.image.tags[0] if container.image.tags else container.image.short_id,
        'status': container.status,
        'state': container.attrs['State'],
        'created': container.attrs['Created'],
        'ports': container.ports,
        'labels': container.labels,
    }
