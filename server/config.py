"""
Configuration Loader with Hot Reload
====================================
Loads YAML configuration with environment-specific overrides and hot reload support
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)

# Global configuration instance
_config: Optional[Dict[str, Any]] = None
_observer: Optional[Observer] = None


class ConfigReloadHandler(FileSystemEventHandler):
    """Handler for configuration file changes"""
    
    def on_modified(self, event):
        if event.src_path.endswith('.yaml') or event.src_path.endswith('.yml'):
            logger.info(f"Configuration file changed: {event.src_path}")
            load_config(reload=True)


def get_config_path() -> Path:
    """Get the path to the configuration directory"""
    config_dir = Path(__file__).parent / "config"
    return config_dir


def load_config(reload: bool = False) -> Dict[str, Any]:
    """
    Load configuration from YAML files with environment-specific overrides
    
    Args:
        reload: Force reload even if config is cached
    
    Returns:
        Dict containing merged configuration
    """
    global _config
    
    # Return cached config if available and not reloading
    if _config is not None and not reload:
        return _config
    
    config_dir = get_config_path()
    env = os.getenv('ENV', 'default')
    
    # Load base configuration
    base_config_path = config_dir / "settings.yaml"
    if not base_config_path.exists():
        raise FileNotFoundError(f"Base configuration not found: {base_config_path}")
    
    with open(base_config_path, 'r') as f:
        config = yaml.safe_load(f) or {}
    
    # Load environment-specific overrides
    if env != 'default':
        env_config_path = config_dir / f"settings.{env}.yaml"
        if env_config_path.exists():
            with open(env_config_path, 'r') as f:
                env_config = yaml.safe_load(f) or {}
            # Deep merge (simple version - top level only)
            for key, value in env_config.items():
                if isinstance(value, dict) and key in config and isinstance(config[key], dict):
                    config[key].update(value)
                else:
                    config[key] = value
            logger.info(f"Loaded environment config: {env}")
    
    # Expand environment variables in config values
    config = _expand_env_vars(config)
    
    _config = config
    logger.info("Configuration loaded successfully")
    return config


def _expand_env_vars(obj: Any) -> Any:
    """Recursively expand environment variables in configuration"""
    if isinstance(obj, dict):
        return {k: _expand_env_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_expand_env_vars(item) for item in obj]
    elif isinstance(obj, str):
        # Support ${VAR:-default} syntax
        import re
        pattern = r'\$\{([^}:]+)(?::-)([^}]+)?\}'
        
        def replacer(match):
            var_name = match.group(1)
            default_value = match.group(2) or ''
            return os.getenv(var_name, default_value)
        
        return re.sub(pattern, replacer, obj)
    else:
        return obj


def get_config() -> Dict[str, Any]:
    """Get the current configuration (loads if not cached)"""
    return load_config()


def start_config_watcher():
    """Start watching configuration files for changes"""
    global _observer
    
    if _observer is not None:
        return  # Already watching
    
    config_dir = get_config_path()
    event_handler = ConfigReloadHandler()
    _observer = Observer()
    _observer.schedule(event_handler, str(config_dir), recursive=False)
    _observer.start()
    logger.info(f"Started watching configuration directory: {config_dir}")


def stop_config_watcher():
    """Stop watching configuration files"""
    global _observer
    
    if _observer is not None:
        _observer.stop()
        _observer.join()
        _observer = None
        logger.info("Stopped configuration watcher")


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate configuration structure
    
    Args:
        config: Configuration dictionary to validate
    
    Returns:
        True if valid
    
    Raises:
        ValueError: If configuration is invalid
    """
    # Required top-level keys
    required_keys = ['server', 'mcp', 'security', 'docker']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required configuration key: {key}")
    
    # Validate server config
    if 'port' not in config['server']:
        raise ValueError("Missing required configuration: server.port")
    
    # Validate MCP config
    if 'name' not in config['mcp']:
        raise ValueError("Missing required configuration: mcp.name")
    
    # Validate security config
    if 'authentication' not in config['security']:
        raise ValueError("Missing required configuration: security.authentication")
    
    auth_config = config['security']['authentication']
    if auth_config.get('enabled', False):
        password = auth_config.get('password', '')
        # Empty string is falsy in Python
        if not password or password.strip() == '':
            raise ValueError("Authentication enabled but no password configured")
    
    # Validate Docker config
    if 'socket_path' not in config['docker']:
        raise ValueError("Missing required configuration: docker.socket_path")
    
    logger.info("Configuration validation passed")
    return True
