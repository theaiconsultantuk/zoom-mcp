"""
Zoom MCP REST API

Simple REST API endpoints for Gumloop integration.
These endpoints wrap the MCP tools to provide easy HTTP access.
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

from zoom_mcp.tools.meetings import (
    ListMeetingsParams,
    GetMeetingParams,
    ListTodaysMeetingsParams,
    list_meetings,
    get_meeting,
    list_todays_meetings,
)
from zoom_mcp.tools.users import (
    ListUsersParams,
    GetUserParams,
    list_users,
    get_user,
)
from zoom_mcp.tools.recordings import (
    ListRecordingsParams,
    GetRecordingTranscriptParams,
    list_recordings,
    get_recording_transcript,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Zoom MCP REST API",
    description="REST API for Zoom MCP Server - Gumloop Integration",
    version="1.0.0"
)


@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "name": "Zoom MCP REST API",
        "version": "1.0.0",
        "endpoints": {
            "meetings": "/api/meetings/today",
            "specific_meeting": "/api/meetings/{meeting_id}",
            "users": "/api/users",
            "recordings": "/api/recordings"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/api/test/sample-meetings")
async def get_sample_meetings():
    """
    Return sample meeting data for testing Gumloop integrations.
    This is dummy data - not real meetings from Zoom.
    """
    return {
        "date": "2025-10-15",
        "total_meetings": 3,
        "meetings": [
            {
                "id": "123456789",
                "topic": "Team Standup",
                "start_time": "2025-10-15T09:00:00Z",
                "duration": 30,
                "user_email": "manager@example.com",
                "user_name": "Project Manager",
                "join_url": "https://zoom.us/j/123456789",
                "agenda": "Daily standup meeting",
                "timezone": "Europe/London"
            },
            {
                "id": "987654321",
                "topic": "Client Demo",
                "start_time": "2025-10-15T14:00:00Z",
                "duration": 60,
                "user_email": "sales@example.com",
                "user_name": "Sales Rep",
                "join_url": "https://zoom.us/j/987654321",
                "agenda": "Product demonstration for new client",
                "timezone": "Europe/London"
            },
            {
                "id": "555555555",
                "topic": "All Hands Meeting",
                "start_time": "2025-10-15T16:00:00Z",
                "duration": 90,
                "user_email": "ceo@example.com",
                "user_name": "CEO",
                "join_url": "https://zoom.us/j/555555555",
                "agenda": "Quarterly company update",
                "timezone": "Europe/London"
            }
        ]
    }


@app.get("/api/meetings/today")
async def get_todays_meetings(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format (default: today)"),
    user_id: Optional[str] = Query(None, description="Filter by user ID or email")
):
    """
    Get all meetings for a specific date (or today if not specified).

    Example:
        GET /api/meetings/today?date=2025-10-15
    """
    try:
        # If date is provided, we need to use list_meetings with date filters
        if date:
            # Validate date format
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

            params = ListMeetingsParams(
                user_id=user_id or "me",
                type="scheduled",
                from_date=date,
                to_date=date,
                page_size=300
            )
            result = await list_meetings(params)

            # Transform to match list_todays_meetings format
            return {
                "date": date,
                "total_meetings": len(result.get("meetings", [])),
                "meetings": result.get("meetings", [])
            }
        else:
            # Use list_todays_meetings for today
            params = ListTodaysMeetingsParams(user_id=user_id)
            return await list_todays_meetings(params)

    except Exception as e:
        logger.error(f"Error getting meetings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/meetings/{meeting_id}")
async def get_meeting_details(meeting_id: str):
    """
    Get details for a specific meeting.

    Example:
        GET /api/meetings/123456789
    """
    try:
        params = GetMeetingParams(meeting_id=meeting_id)
        return await get_meeting(params)
    except Exception as e:
        logger.error(f"Error getting meeting {meeting_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/users")
async def get_users(
    status: str = Query("active", description="User status: active, inactive, or pending")
):
    """
    Get list of all users in the Zoom account.

    Example:
        GET /api/users?status=active
    """
    try:
        params = ListUsersParams(status=status)
        return await list_users(params)
    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/users/{user_id}")
async def get_user_details(user_id: str):
    """
    Get details for a specific user.

    Example:
        GET /api/users/user@example.com
    """
    try:
        params = GetUserParams(user_id=user_id)
        return await get_user(params)
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/recordings")
async def get_recordings(
    from_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    to_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    user_id: Optional[str] = Query(None, description="Filter by user ID or email")
):
    """
    Get list of cloud recordings.

    Example:
        GET /api/recordings?from_date=2025-10-01&to_date=2025-10-15
    """
    try:
        params = ListRecordingsParams(
            from_date=from_date,
            to_date=to_date,
            user_id=user_id
        )
        return await list_recordings(params)
    except Exception as e:
        logger.error(f"Error listing recordings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/recordings/{recording_id}/transcript")
async def get_transcript(recording_id: str):
    """
    Get transcript for a specific recording.

    Example:
        GET /api/recordings/abc123/transcript
    """
    try:
        params = GetRecordingTranscriptParams(recording_id=recording_id)
        return await get_recording_transcript(params)
    except Exception as e:
        logger.error(f"Error getting transcript for {recording_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)
