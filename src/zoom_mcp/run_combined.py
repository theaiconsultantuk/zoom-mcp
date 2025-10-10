"""
Combined server runner - starts both MCP SSE and REST API servers.
"""

import asyncio
import logging
import os
import signal
import sys
from multiprocessing import Process

import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def run_mcp_server():
    """Run the MCP SSE server."""
    from zoom_mcp.server import create_zoom_mcp

    try:
        mcp_server = create_zoom_mcp()
        transport = os.getenv("MCP_TRANSPORT", "sse")
        logger.info(f"Starting MCP SSE server on port 3000")
        mcp_server.start(transport=transport)
    except Exception as e:
        logger.error(f"Error starting MCP server: {str(e)}")
        sys.exit(1)


def run_rest_api():
    """Run the REST API server."""
    try:
        logger.info(f"Starting REST API server on port 3001")
        uvicorn.run(
            "zoom_mcp.api:app",
            host="0.0.0.0",
            port=3001,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Error starting REST API: {str(e)}")
        sys.exit(1)


def main():
    """Start both servers in parallel."""
    logger.info("=" * 60)
    logger.info("Starting Zoom MCP Combined Server")
    logger.info("- MCP SSE Server: http://0.0.0.0:3000/sse")
    logger.info("- REST API:       http://0.0.0.0:3001/api/")
    logger.info("=" * 60)

    # Start MCP server in a separate process
    mcp_process = Process(target=run_mcp_server, name="MCP-SSE-Server")
    mcp_process.start()

    # Start REST API in a separate process
    api_process = Process(target=run_rest_api, name="REST-API-Server")
    api_process.start()

    def signal_handler(sig, frame):
        """Handle shutdown signals."""
        logger.info("\nShutting down servers...")
        mcp_process.terminate()
        api_process.terminate()
        mcp_process.join()
        api_process.join()
        sys.exit(0)

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Wait for both processes
    try:
        mcp_process.join()
        api_process.join()
    except KeyboardInterrupt:
        logger.info("\nShutting down servers...")
        mcp_process.terminate()
        api_process.terminate()
        mcp_process.join()
        api_process.join()


if __name__ == "__main__":
    main()
