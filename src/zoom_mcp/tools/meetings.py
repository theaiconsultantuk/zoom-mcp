"""
Zoom Meetings Tools

This module provides tools for working with Zoom meetings.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from zoom_mcp.auth.zoom_auth import ZoomAuth

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class ListMeetingsParams(BaseModel):
    """Parameters for listing meetings."""
    user_id: Optional[str] = Field(None, description="User ID or email. Use 'me' for authenticated user")
    type: str = Field("scheduled", description="Meeting type: scheduled, live, or upcoming")
    page_size: int = Field(30, description="Number of records per page (max 300)")
    from_date: Optional[str] = Field(None, description="Start date in YYYY-MM-DD format")
    to_date: Optional[str] = Field(None, description="End date in YYYY-MM-DD format")


class GetMeetingParams(BaseModel):
    """Parameters for getting meeting details."""
    meeting_id: str = Field(..., description="Meeting ID")


class ListTodaysMeetingsParams(BaseModel):
    """Parameters for listing today's meetings."""
    user_id: Optional[str] = Field(None, description="User ID or email. Leave empty to get all users' meetings")


async def list_meetings(params: ListMeetingsParams) -> Dict[str, Any]:
    """
    List Zoom meetings for a user.

    Args:
        params: Parameters for listing meetings

    Returns:
        Dict containing the list of meetings
    """
    try:
        # Initialize Zoom auth from environment variables
        zoom_auth = ZoomAuth.from_env()

        # Get the access token
        access_token = zoom_auth.get_access_token()

        # Determine user ID
        user_id = params.user_id or "me"

        # Construct the API URL
        api_url = f"https://api.zoom.us/v2/users/{user_id}/meetings"

        # Build query parameters
        query_params = {
            "type": params.type,
            "page_size": params.page_size
        }

        if params.from_date:
            query_params["from"] = params.from_date
        if params.to_date:
            query_params["to"] = params.to_date

        # Make the API request
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, headers=headers, params=query_params)

            if response.status_code != 200:
                error_message = f"Failed to list meetings: {response.status_code} - {response.text}"
                logger.error(error_message)
                raise Exception(error_message)

            return response.json()

    except Exception as e:
        logger.error(f"Error listing meetings: {str(e)}")
        raise


async def get_meeting(params: GetMeetingParams) -> Dict[str, Any]:
    """
    Get details for a specific meeting.

    Args:
        params: Parameters for getting meeting details

    Returns:
        Dict containing meeting details
    """
    try:
        # Initialize Zoom auth from environment variables
        zoom_auth = ZoomAuth.from_env()

        # Get the access token
        access_token = zoom_auth.get_access_token()

        # Construct the API URL
        api_url = f"https://api.zoom.us/v2/meetings/{params.meeting_id}"

        # Make the API request
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, headers=headers)

            if response.status_code != 200:
                error_message = f"Failed to get meeting: {response.status_code} - {response.text}"
                logger.error(error_message)
                raise Exception(error_message)

            return response.json()

    except Exception as e:
        logger.error(f"Error getting meeting: {str(e)}")
        raise


async def list_todays_meetings(params: ListTodaysMeetingsParams) -> Dict[str, Any]:
    """
    List all meetings for today.

    Args:
        params: Parameters for listing today's meetings

    Returns:
        Dict containing today's meetings
    """
    try:
        # Initialize Zoom auth from environment variables
        zoom_auth = ZoomAuth.from_env()

        # Get the access token
        access_token = zoom_auth.get_access_token()

        # Get today's date range
        today = datetime.now().strftime("%Y-%m-%d")

        # If user_id is provided, get meetings for that user
        if params.user_id:
            api_url = f"https://api.zoom.us/v2/users/{params.user_id}/meetings"
            query_params = {
                "type": "scheduled",
                "from": today,
                "to": today,
                "page_size": 300
            }
        else:
            # Get list of users first
            users_url = "https://api.zoom.us/v2/users"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            import httpx
            all_meetings = []

            async with httpx.AsyncClient() as client:
                # Get all users
                users_response = await client.get(
                    users_url,
                    headers=headers,
                    params={"page_size": 300}
                )

                if users_response.status_code != 200:
                    error_message = f"Failed to list users: {users_response.status_code} - {users_response.text}"
                    logger.error(error_message)
                    raise Exception(error_message)

                users_data = users_response.json()

                # Get meetings for each user
                for user in users_data.get("users", []):
                    user_id = user.get("id")
                    meetings_url = f"https://api.zoom.us/v2/users/{user_id}/meetings"

                    meetings_response = await client.get(
                        meetings_url,
                        headers=headers,
                        params={
                            "type": "upcoming",  # Changed to 'upcoming' to include recurring meetings
                            "from": today,
                            "to": today,
                            "page_size": 300
                        }
                    )

                    if meetings_response.status_code == 200:
                        meetings_data = meetings_response.json()
                        meetings = meetings_data.get("meetings", [])
                        # Add user info to each meeting
                        for meeting in meetings:
                            meeting["user_email"] = user.get("email")
                            meeting["user_name"] = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
                        all_meetings.extend(meetings)

                return {
                    "date": today,
                    "total_meetings": len(all_meetings),
                    "meetings": all_meetings
                }

        # If user_id was provided
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, headers=headers, params=query_params)

            if response.status_code != 200:
                error_message = f"Failed to list meetings: {response.status_code} - {response.text}"
                logger.error(error_message)
                raise Exception(error_message)

            data = response.json()
            data["date"] = today
            return data

    except Exception as e:
        logger.error(f"Error listing today's meetings: {str(e)}")
        raise
