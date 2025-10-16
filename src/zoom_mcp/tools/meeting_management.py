"""
Meeting Management Tools

Update, cancel, and search meetings with natural language support.
"""

import httpx
from pydantic import BaseModel, Field
from typing import Optional, List

from zoom_mcp.auth.zoom_auth import ZoomAuth


class UpdateMeetingParams(BaseModel):
    """Parameters for updating a meeting."""
    meeting_id: str = Field(description="Meeting ID to update")
    topic: Optional[str] = Field(None, description="New meeting topic")
    start_time: Optional[str] = Field(None, description="New start time (ISO format)")
    duration: Optional[int] = Field(None, description="New duration in minutes")
    agenda: Optional[str] = Field(None, description="New agenda")


class DeleteMeetingParams(BaseModel):
    """Parameters for deleting a meeting."""
    meeting_id: str = Field(description="Meeting ID to delete")


async def update_meeting(params: UpdateMeetingParams) -> dict:
    """
    Update an existing Zoom meeting.

    Args:
        params: Update parameters

    Returns:
        Updated meeting details
    """
    zoom_auth = ZoomAuth.from_env()
    access_token = zoom_auth.get_access_token()

    api_url = f"https://api.zoom.us/v2/meetings/{params.meeting_id}"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Build update payload
    update_data = {}
    if params.topic:
        update_data["topic"] = params.topic
    if params.start_time:
        update_data["start_time"] = params.start_time
    if params.duration:
        update_data["duration"] = params.duration
    if params.agenda:
        update_data["agenda"] = params.agenda

    async with httpx.AsyncClient() as client:
        response = await client.patch(api_url, headers=headers, json=update_data)

        if response.status_code != 204:  # Zoom returns 204 No Content on success
            return {
                "error": f"Failed to update meeting: {response.status_code}",
                "message": response.text
            }

        # Get updated meeting details
        get_response = await client.get(api_url, headers=headers)
        return get_response.json() if get_response.status_code == 200 else {"success": True}


async def delete_meeting(params: DeleteMeetingParams) -> dict:
    """
    Delete/cancel a Zoom meeting.

    Args:
        params: Delete parameters

    Returns:
        Success status
    """
    zoom_auth = ZoomAuth.from_env()
    access_token = zoom_auth.get_access_token()

    api_url = f"https://api.zoom.us/v2/meetings/{params.meeting_id}"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    async with httpx.AsyncClient() as client:
        response = await client.delete(api_url, headers=headers)

        if response.status_code != 204:
            return {
                "error": f"Failed to delete meeting: {response.status_code}",
                "message": response.text
            }

        return {
            "success": True,
            "meeting_id": params.meeting_id,
            "message": "Meeting deleted successfully"
        }


async def find_meeting_by_description(
    description: str,
    user_id: Optional[str] = None
) -> Optional[dict]:
    """
    Find a meeting by natural language description.

    Args:
        description: Description like "my meeting with Agostino" or "think tank meeting"
        user_id: Optional user ID to search

    Returns:
        Meeting details if found, None otherwise
    """
    from zoom_mcp.tools.meetings import list_meetings, ListMeetingsParams

    # Get all upcoming meetings
    params = ListMeetingsParams(
        user_id=user_id or "me",
        type="upcoming",
        page_size=100
    )

    meetings_data = await list_meetings(params)
    meetings = meetings_data.get("meetings", [])

    description_lower = description.lower()

    # Search by topic or attendee name
    for meeting in meetings:
        topic = meeting.get("topic", "").lower()

        if description_lower in topic:
            return meeting

    return None
