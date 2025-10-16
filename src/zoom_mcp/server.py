"""
Zoom MCP Server

This module provides the main implementation of the Zoom MCP server.
"""

import os
import json
import logging

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from zoom_mcp.auth.zoom_auth import ZoomAuth
from zoom_mcp.resources.recordings import RecordingListParams, RecordingResource
from zoom_mcp.tools.recordings import (
    GetRecordingTranscriptParams,
    ListRecordingsParams,
    get_recording_transcript as get_recording_transcript_tool,
    list_recordings as list_recordings_tool,
)
from zoom_mcp.tools.meetings import (
    ListMeetingsParams,
    GetMeetingParams,
    ListTodaysMeetingsParams,
    list_meetings as list_meetings_tool,
    get_meeting as get_meeting_tool,
    list_todays_meetings as list_todays_meetings_tool,
)
from zoom_mcp.tools.users import (
    ListUsersParams,
    GetUserParams,
    list_users as list_users_tool,
    get_user as get_user_tool,
)
from zoom_mcp.tools.contacts import (
    ListContactsParams,
    GetContactParams,
    list_contacts as list_contacts_tool,
    get_contact as get_contact_tool,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class ZoomMCP:
    """
    Zoom MCP Server implementation.

    This class provides a Model Context Protocol (MCP) server for Zoom,
    allowing LLMs to interact with Zoom data and functionality.
    """

    def __init__(self):
        """Initialize the Zoom MCP server."""
        try:
            # Initialize auth manager from environment variables
            self.auth_manager = ZoomAuth.from_env()
            
            self.mcp_server = FastMCP("Zoom")
            # Add name attribute for MCP CLI
            self.name = "Zoom"

            # Register resources and tools
            self._register_resources()
            self._register_tools()
        except Exception as e:
            logger.error(f"Error initializing Zoom MCP server: {str(e)}")
            raise

    def _register_resources(self):
        """Register all Zoom resources with the MCP server."""
        # Register recording resources
        recording_resource = RecordingResource(self.auth_manager)

        @self.mcp_server.resource("recordings://list")
        async def list_recordings() -> str:
            """List recordings from Zoom"""
            # Since there's no URI parameter, we pass an empty params object
            recordings = await recording_resource.list_recordings(RecordingListParams())
            return json.dumps(recordings)

        @self.mcp_server.resource("recording://{recording_id}")
        async def get_recording(recording_id: str) -> str:
            """Get a specific recording from Zoom"""
            recording = await recording_resource.get_recording(recording_id)
            return json.dumps(recording)

    def _register_tools(self):
        """Register all Zoom tools with the MCP server."""

        # Recording tools
        @self.mcp_server.tool()
        async def get_recording_transcript(params: GetRecordingTranscriptParams) -> str:
            """
            Get the transcript for a Zoom recording.

            Args:
                params: Parameters for retrieving the recording transcript

            Returns:
                JSON string containing the transcript data
            """
            try:
                transcript_data = await get_recording_transcript_tool(params)
                return json.dumps(transcript_data.dict())
            except Exception as e:
                logger.error(f"Error in get_recording_transcript tool: {str(e)}")
                raise

        @self.mcp_server.tool()
        async def list_recordings(params: ListRecordingsParams) -> str:
            """
            List Zoom cloud recordings.

            Args:
                params: Parameters for listing recordings

            Returns:
                JSON string containing the list of recordings
            """
            try:
                recordings_data = await list_recordings_tool(params)
                return json.dumps(recordings_data)
            except Exception as e:
                logger.error(f"Error in list_recordings tool: {str(e)}")
                raise

        # Meeting tools
        @self.mcp_server.tool()
        async def list_meetings(params: ListMeetingsParams) -> str:
            """
            List Zoom meetings for a user.

            Args:
                params: Parameters for listing meetings

            Returns:
                JSON string containing the list of meetings
            """
            try:
                meetings_data = await list_meetings_tool(params)
                return json.dumps(meetings_data)
            except Exception as e:
                logger.error(f"Error in list_meetings tool: {str(e)}")
                raise

        @self.mcp_server.tool()
        async def get_meeting(params: GetMeetingParams) -> str:
            """
            Get details for a specific Zoom meeting.

            Args:
                params: Parameters for getting meeting details

            Returns:
                JSON string containing meeting details
            """
            try:
                meeting_data = await get_meeting_tool(params)
                return json.dumps(meeting_data)
            except Exception as e:
                logger.error(f"Error in get_meeting tool: {str(e)}")
                raise

        @self.mcp_server.tool()
        async def list_todays_meetings(params: ListTodaysMeetingsParams) -> str:
            """
            List all Zoom meetings scheduled for today.

            Args:
                params: Parameters for listing today's meetings

            Returns:
                JSON string containing today's meetings
            """
            try:
                meetings_data = await list_todays_meetings_tool(params)
                return json.dumps(meetings_data)
            except Exception as e:
                logger.error(f"Error in list_todays_meetings tool: {str(e)}")
                raise

        # User tools
        @self.mcp_server.tool()
        async def list_users(params: ListUsersParams) -> str:
            """
            List Zoom users in the account.

            Args:
                params: Parameters for listing users

            Returns:
                JSON string containing the list of users
            """
            try:
                users_data = await list_users_tool(params)
                return json.dumps(users_data)
            except Exception as e:
                logger.error(f"Error in list_users tool: {str(e)}")
                raise

        @self.mcp_server.tool()
        async def get_user(params: GetUserParams) -> str:
            """
            Get details for a specific Zoom user.

            Args:
                params: Parameters for getting user details

            Returns:
                JSON string containing user details
            """
            try:
                user_data = await get_user_tool(params)
                return json.dumps(user_data)
            except Exception as e:
                logger.error(f"Error in get_user tool: {str(e)}")
                raise

        # Contact tools
        @self.mcp_server.tool()
        async def list_contacts(params: ListContactsParams) -> str:
            """
            List Zoom contacts for the authenticated user.

            Args:
                params: Parameters for listing contacts

            Returns:
                JSON string containing the list of contacts
            """
            try:
                contacts_data = await list_contacts_tool(params)
                return json.dumps(contacts_data)
            except Exception as e:
                logger.error(f"Error in list_contacts tool: {str(e)}")
                raise

        @self.mcp_server.tool()
        async def get_contact(params: GetContactParams) -> str:
            """
            Get details for a specific Zoom contact.

            Args:
                params: Parameters for getting contact details

            Returns:
                JSON string containing contact details
            """
            try:
                contact_data = await get_contact_tool(params)
                return json.dumps(contact_data)
            except Exception as e:
                logger.error(f"Error in get_contact tool: {str(e)}")
                raise

    def start(self, transport: str = "stdio"):
        """
        Start the MCP server.

        Args:
            transport: Transport mode - "stdio" for local, "sse" for remote HTTP/SSE

        Note:
            For SSE transport, configure host and port via environment variables:
            - FASTMCP_HOST (default: "0.0.0.0")
            - FASTMCP_PORT (default: 8000)
        """
        if transport == "sse":
            host = os.getenv("FASTMCP_HOST", "0.0.0.0")
            port = os.getenv("FASTMCP_PORT", "8080")
            logger.info(f"Starting MCP server in SSE mode on {host}:{port}")
            self.mcp_server.run(transport="sse")
        else:
            logger.info("Starting MCP server in stdio mode")
            self.mcp_server.run()

    def stop(self):
        """Stop the MCP server."""
        # Cleanup resources if needed
        pass


def create_zoom_mcp() -> ZoomMCP:
    """
    Create and configure a Zoom MCP server instance.
    
    Returns:
        Configured ZoomMCP instance
    """
    return ZoomMCP()


# Create a standard variable that MCP CLI can recognize
# This will be used when running `mcp install src/zoom_mcp/server.py`
# The actual configuration will be loaded from environment variables

# Load environment variables from .env file
load_dotenv()

# Create the server instance with a standard variable name
# This is the variable that MCP CLI will look for
try:
    server = create_zoom_mcp()
except Exception as e:
    logger.error(f"Error creating Zoom MCP server: {str(e)}")
    # Create a placeholder server for MCP CLI discovery
    # The actual server will be created when run with proper environment variables
    server = None


if __name__ == "__main__":
    try:
        # Create and start the MCP server
        mcp_server = create_zoom_mcp()

        # Get transport mode from environment (default to sse for Docker deployment)
        transport = os.getenv("MCP_TRANSPORT", "sse")

        # Run the server
        mcp_server.start(transport=transport)
    except Exception as e:
        logger.error(f"Error starting Zoom MCP server: {str(e)}")
        import sys
        sys.exit(1) 