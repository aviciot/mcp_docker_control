"""
Auto-Discovery Utility
=====================
Automatically imports modules from tools/, resources/, and prompts/ directories
"""

import logging
import importlib
from pathlib import Path

logger = logging.getLogger(__name__)


def auto_discover_modules():
    """
    Auto-discover and import all tool, resource, and prompt modules
    """
    base_dir = Path(__file__).parent.parent
    
    # Directories to scan
    directories = ['tools', 'resources', 'prompts']
    
    for directory in directories:
        dir_path = base_dir / directory
        if not dir_path.exists():
            logger.warning(f"Directory not found: {dir_path}")
            continue
        
        # Find all .py files (except __init__.py and files starting with _)
        for file_path in dir_path.glob('*.py'):
            if file_path.name == '__init__.py' or file_path.name.startswith('_'):
                continue
            
            # Import the module
            module_name = f"{directory}.{file_path.stem}"
            try:
                importlib.import_module(module_name)
                logger.info(f"✅ Loaded: {module_name}")
            except Exception as e:
                logger.error(f"❌ Failed to load {module_name}: {e}")
