"""
Docker Control MCP Application - FastMCP Instance
=================================================
Main MCP server using FastMCP framework for Docker container management
"""

import logging
from fastmcp import FastMCP

from config import get_config

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load configuration
config = get_config()

# Create FastMCP instance
mcp = FastMCP(
    name=config.get('mcp', {}).get('name', 'docker-control')
)

logger.info(f"Initializing {mcp.name}")
