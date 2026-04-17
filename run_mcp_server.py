"""
Run the MCP server locally for development and testing.
"""

import logging
import os
from utils import setup_logging
from mcp_server.app import app
import uvicorn

if __name__ == "__main__":
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting MCP Server for local development...")
    logger.info("API documentation available at: http://localhost:8000/docs")
    logger.info("MCP documentation available at: http://localhost:8000/docs-mcp")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
