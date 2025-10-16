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
from zoom_mcp.tools.contacts import (
    ListContactsParams,
    GetContactParams,
    list_contacts,
    get_contact,
)
from zoom_mcp.tools.personal_contacts import (
    SearchContactParams,
    search_personal_contacts,
    get_contact_by_name,
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
            "recordings": "/api/recordings",
            "contacts": "/api/contacts"
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

            # If no user_id specified, use list_todays_meetings which gets all users
            if not user_id:
                params = ListTodaysMeetingsParams(user_id=None)
                # Override the date in the function
                import httpx
                from zoom_mcp.auth.zoom_auth import ZoomAuth

                zoom_auth = ZoomAuth.from_env()
                access_token = zoom_auth.get_access_token()

                # Get list of users first
                users_url = "https://api.zoom.us/v2/users"
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }

                all_meetings = []
                async with httpx.AsyncClient() as client:
                    users_response = await client.get(
                        users_url,
                        headers=headers,
                        params={"page_size": 300}
                    )

                    if users_response.status_code == 200:
                        users_data = users_response.json()

                        # Get meetings for each user
                        for user in users_data.get("users", []):
                            user_id_item = user.get("id")
                            meetings_url = f"https://api.zoom.us/v2/users/{user_id_item}/meetings"

                            meetings_response = await client.get(
                                meetings_url,
                                headers=headers,
                                params={
                                    "type": "upcoming",  # Changed from 'scheduled' to 'upcoming' to include recurring meetings
                                    "from": date,
                                    "to": date,
                                    "page_size": 300
                                }
                            )

                            if meetings_response.status_code == 200:
                                meetings_data = meetings_response.json()
                                meetings = meetings_data.get("meetings", [])
                                for meeting in meetings:
                                    meeting["user_email"] = user.get("email")
                                    meeting["user_name"] = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
                                all_meetings.extend(meetings)

                return {
                    "date": date,
                    "total_meetings": len(all_meetings),
                    "meetings": all_meetings
                }
            else:
                params = ListMeetingsParams(
                    user_id=user_id,
                    type="upcoming",  # Changed from 'scheduled' to 'upcoming' to include recurring meetings
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


@app.get("/api/meetings/templates")
async def get_meeting_templates():
    """
    Get available meeting templates.

    Returns:
        Dictionary of meeting templates (think_tank, ai_training, office_hours, etc.)
    """
    import json
    from pathlib import Path

    try:
        template_file = Path(__file__).parent.parent.parent / "meeting_templates.json"
        if template_file.exists():
            with open(template_file, 'r') as f:
                templates = json.load(f)
            return {"success": True, "templates": templates}
        else:
            return {
                "success": True,
                "templates": {
                    "think_tank": {
                        "topic": "Weekly Thinktank Meeting",
                        "duration": 90,
                        "agenda": "Weekly discussion"
                    }
                }
            }
    except Exception as e:
        logger.error(f"Error loading templates: {str(e)}")
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


@app.get("/api/meetings/{meeting_id}/past")
async def get_past_meeting(meeting_id: str):
    """
    Get details of the last past instance of a meeting.
    Use this to get the UUID of past occurrences for recurring meetings.

    Example:
        GET /api/meetings/87047461484/past
    """
    try:
        from zoom_mcp.auth.zoom_auth import ZoomAuth
        import httpx

        zoom_auth = ZoomAuth.from_env()
        access_token = zoom_auth.get_access_token()

        api_url = f"https://api.zoom.us/v2/past_meetings/{meeting_id}"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, headers=headers)

            if response.status_code != 200:
                error_message = f"Failed to get past meeting: {response.status_code} - {response.text}"
                logger.error(error_message)
                raise HTTPException(status_code=response.status_code, detail=error_message)

            return response.json()

    except Exception as e:
        logger.error(f"Error getting past meeting {meeting_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/meetings/{meeting_id}/summary")
async def get_meeting_summary(meeting_id: str):
    """
    Get AI-generated summary for a specific meeting.

    This retrieves the Zoom AI Companion meeting summary including:
    - Summary overview
    - Next steps
    - Action items
    - Key points

    Example:
        GET /api/meetings/87047461484/summary

    Note: Requires meeting:read:meeting_summary scope to be enabled
    """
    try:
        from zoom_mcp.auth.zoom_auth import ZoomAuth
        import httpx

        # Get auth token
        zoom_auth = ZoomAuth.from_env()
        access_token = zoom_auth.get_access_token()

        # Construct API URL
        api_url = f"https://api.zoom.us/v2/meetings/{meeting_id}/meeting_summary"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, headers=headers)

            if response.status_code == 404:
                return {
                    "meeting_id": meeting_id,
                    "summary_available": False,
                    "message": "No AI summary available for this meeting yet. Summaries are generated after the meeting ends."
                }

            if response.status_code != 200:
                error_message = f"Failed to get meeting summary: {response.status_code} - {response.text}"
                logger.error(error_message)
                raise HTTPException(status_code=response.status_code, detail=error_message)

            summary_data = response.json()
            return {
                "meeting_id": meeting_id,
                "summary_available": True,
                **summary_data
            }

    except Exception as e:
        logger.error(f"Error getting meeting summary for {meeting_id}: {str(e)}")
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


@app.post("/api/meetings/create-from-template")
async def create_meeting_from_template(
    template: str = Query(..., description="Template name (think_tank, ai_training, etc.)"),
    start_time: str = Query(..., description="Start time in ISO format (YYYY-MM-DDTHH:MM:SSZ)"),
    attendees: Optional[str] = Query(None, description="Comma-separated email addresses to add to template defaults"),
    override_topic: Optional[str] = Query(None, description="Override the template topic"),
    override_duration: Optional[int] = Query(None, description="Override the template duration")
):
    """
    Create a meeting from a template.

    Example:
        POST /api/meetings/create-from-template?template=think_tank&start_time=2025-10-16T19:00:00Z&attendees=oliver@example.com,milana@example.com

    This is perfect for AIVA - just specify template and time!
    """
    try:
        # Get templates
        templates_response = await get_meeting_templates()
        templates = templates_response.get("templates", {})

        if template not in templates:
            raise HTTPException(
                status_code=404,
                detail=f"Template '{template}' not found. Available: {', '.join(templates.keys())}"
            )

        template_data = templates[template]

        # Build meeting from template
        topic = override_topic or template_data.get("topic")
        duration = override_duration or template_data.get("duration", 60)
        agenda = template_data.get("agenda", "")

        # Combine template attendees with specified attendees
        template_attendees = template_data.get("default_attendees", [])
        if attendees:
            template_attendees.extend(attendees.split(","))

        attendees_str = ",".join(template_attendees) if template_attendees else None

        # Create the meeting
        return await create_meeting(
            topic=topic,
            start_time=start_time,
            duration=duration,
            attendees=attendees_str,
            agenda=agenda
        )

    except Exception as e:
        logger.error(f"Error creating meeting from template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/meetings/create")
async def create_meeting(
    topic: str = Query(..., description="Meeting topic/title"),
    start_time: str = Query(..., description="Start time in ISO format (YYYY-MM-DDTHH:MM:SSZ)"),
    duration: int = Query(60, description="Duration in minutes"),
    attendees: Optional[str] = Query(None, description="Comma-separated email addresses"),
    agenda: Optional[str] = Query(None, description="Meeting agenda"),
    user_id: Optional[str] = Query(None, description="Host user ID (defaults to main account)")
):
    """
    Create a new Zoom meeting.

    Example:
        POST /api/meetings/create?topic=Think Tank Meeting&start_time=2025-10-16T19:00:00Z&duration=90&attendees=oliver@example.com,milana@example.com

    Returns:
        Meeting details including join URL and meeting ID
    """
    try:
        from zoom_mcp.auth.zoom_auth import ZoomAuth
        import httpx

        zoom_auth = ZoomAuth.from_env()
        access_token = zoom_auth.get_access_token()

        # If no user_id specified, get the first user from the account
        if not user_id:
            users_response = await get_users(status="active")
            if users_response.get("users"):
                user_id = users_response["users"][0]["id"]
            else:
                raise HTTPException(status_code=400, detail="No users found in account")

        # Construct API URL
        api_url = f"https://api.zoom.us/v2/users/{user_id}/meetings"

        # Build meeting payload
        meeting_data = {
            "topic": topic,
            "type": 2,  # Scheduled meeting
            "start_time": start_time,
            "duration": duration,
            "timezone": "Europe/London",
            "agenda": agenda or "",
            "settings": {
                "host_video": True,
                "participant_video": True,
                "join_before_host": False,
                "mute_upon_entry": False,
                "waiting_room": True,
                "audio": "both",
                "auto_recording": "cloud"
            }
        }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(api_url, headers=headers, json=meeting_data)

            if response.status_code not in [200, 201]:
                error_message = f"Failed to create meeting: {response.status_code} - {response.text}"
                logger.error(error_message)
                raise HTTPException(status_code=response.status_code, detail=error_message)

            meeting_response = response.json()

            # If attendees specified, add them as alternative hosts or send invites
            # (Note: Zoom API doesn't directly add participants, they're invited via email)
            if attendees:
                meeting_response["invited_attendees"] = attendees.split(",")

            return {
                "success": True,
                "meeting_id": meeting_response.get("id"),
                "join_url": meeting_response.get("join_url"),
                "start_url": meeting_response.get("start_url"),
                "topic": meeting_response.get("topic"),
                "start_time": meeting_response.get("start_time"),
                "duration": meeting_response.get("duration"),
                "password": meeting_response.get("password"),
                "full_response": meeting_response
            }

    except Exception as e:
        logger.error(f"Error creating meeting: {str(e)}")
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


@app.get("/api/contacts")
async def get_contacts(
    type: Optional[str] = Query(None, description="Contact type: 'company' for company directory"),
    page_size: Optional[int] = Query(50, description="Number of contacts per page (max 50)")
):
    """
    Get list of Zoom contacts.

    Example:
        GET /api/contacts
        GET /api/contacts?type=company
    """
    try:
        params = ListContactsParams(type=type, page_size=page_size)
        return await list_contacts(params)
    except Exception as e:
        logger.error(f"Error listing contacts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/contacts/{contact_id}")
async def get_contact_details(contact_id: str):
    """
    Get details for a specific contact.

    Example:
        GET /api/contacts/user@example.com
    """
    try:
        params = GetContactParams(contact_id=contact_id)
        return await get_contact(params)
    except Exception as e:
        logger.error(f"Error getting contact {contact_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/contacts/search/{query}")
async def search_contacts(query: str):
    """
    Search personal contacts by name, email, or company.

    Example:
        GET /api/contacts/search/Agostino
        GET /api/contacts/search/ThinkTank
    """
    try:
        params = SearchContactParams(query=query)
        return await search_personal_contacts(params)
    except Exception as e:
        logger.error(f"Error searching contacts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/meetings/book-with-contact")
async def book_meeting_with_contact(
    contact_name: str = Query(..., description="Contact name to invite"),
    topic: str = Query(..., description="Meeting topic"),
    start_time: str = Query(..., description="Start time in ISO format (YYYY-MM-DDTHH:MM:SSZ)"),
    duration: int = Query(60, description="Duration in minutes"),
    agenda: Optional[str] = Query(None, description="Meeting agenda")
):
    """
    Book a meeting with a personal contact by name.

    Example:
        POST /api/meetings/book-with-contact?contact_name=Agostino&topic=Strategy%20Discussion&start_time=2025-10-22T10:00:00Z&duration=60

    Natural language examples that this enables:
        - "Book a meeting with Agostino for Tuesday at 10am"
        - "Schedule call with Milana next week"
        - "Create meeting with Oliver tomorrow"
    """
    try:
        # Look up contact
        contact = await get_contact_by_name(contact_name)

        if not contact:
            raise HTTPException(
                status_code=404,
                detail=f"Contact '{contact_name}' not found in personal contacts"
            )

        # Create meeting with contact's email
        return await create_meeting(
            topic=topic,
            start_time=start_time,
            duration=duration,
            attendees=contact['email'],
            agenda=agenda or f"Meeting with {contact['name']}"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error booking meeting with contact: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)
