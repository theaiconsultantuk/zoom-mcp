"""
Zoom Recordings Tool

This module provides tools for working with Zoom recordings, including
retrieving and processing recording transcripts.
"""

import logging
import re
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


class GetRecordingTranscriptParams(BaseModel):
    """Parameters for retrieving a recording transcript."""
    recording_url: str = Field(..., description="URL of the Zoom recording")
    include_speaker_labels: bool = Field(True, description="Include speaker labels in the transcript")


class ListRecordingsParams(BaseModel):
    """Parameters for listing recordings."""
    user_id: Optional[str] = Field(None, description="User ID or email. Leave empty to get all account recordings")
    from_date: Optional[str] = Field(None, description="Start date in YYYY-MM-DD format")
    to_date: Optional[str] = Field(None, description="End date in YYYY-MM-DD format")
    page_size: int = Field(30, description="Number of records per page (max 300)")


class RecordingTranscriptResponse(BaseModel):
    """Response model for recording transcript."""
    transcript: List[Dict[str, Any]] = Field(..., description="List of transcript segments")
    recording_id: str = Field(..., description="ID of the recording")
    duration: int = Field(..., description="Duration of the recording in seconds")


def extract_recording_id(recording_url: str) -> str:
    """
    Extract the recording ID from a Zoom recording URL.
    
    Args:
        recording_url: The URL of the Zoom recording
        
    Returns:
        The recording ID
        
    Raises:
        ValueError: If the recording ID cannot be extracted from the URL
    """
    # Example URL: https://zoom.us/rec/share/abcdef123456
    pattern = r"zoom\.us/rec/(?:share|play)/([a-zA-Z0-9_-]+)"
    match = re.search(pattern, recording_url)
    
    if not match:
        raise ValueError(f"Could not extract recording ID from URL: {recording_url}")
    
    return match.group(1)


async def get_recording_transcript(params: GetRecordingTranscriptParams) -> RecordingTranscriptResponse:
    """
    Retrieve the transcript for a Zoom recording.
    
    Args:
        params: Parameters for retrieving the recording transcript
        
    Returns:
        The recording transcript response
        
    Raises:
        Exception: If the transcript cannot be retrieved
    """
    try:
        recording_id = extract_recording_id(params.recording_url)
        logger.info(f"Retrieving transcript for recording ID: {recording_id}")
        
        # Initialize Zoom auth from environment variables
        zoom_auth = ZoomAuth.from_env()
        
        # Get the access token
        access_token = await zoom_auth.get_access_token()
        
        # Construct the API URL for retrieving the recording transcript
        account_id = zoom_auth.account_id
        api_url = f"https://api.zoom.us/v2/accounts/{account_id}/recordings/{recording_id}/transcript"
        
        # Make the API request
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Use httpx for async HTTP requests
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, headers=headers)
            
            if response.status_code != 200:
                error_message = f"Failed to retrieve transcript: {response.status_code} - {response.text}"
                logger.error(error_message)
                raise Exception(error_message)
            
            data = response.json()
            
            # Process the transcript data
            transcript_segments = []
            for segment in data.get("recording_transcripts", []):
                transcript_segment = {
                    "start_time": segment.get("start_time"),
                    "end_time": segment.get("end_time"),
                    "text": segment.get("text"),
                }
                
                if params.include_speaker_labels and "speaker" in segment:
                    transcript_segment["speaker"] = segment.get("speaker")
                
                transcript_segments.append(transcript_segment)
            
            # Create the response
            return RecordingTranscriptResponse(
                transcript=transcript_segments,
                recording_id=recording_id,
                duration=data.get("duration", 0)
            )
    
    except Exception as e:
        logger.error(f"Error retrieving recording transcript: {str(e)}")
        raise


async def list_recordings(params: ListRecordingsParams) -> Dict[str, Any]:
    """
    List Zoom recordings.

    Args:
        params: Parameters for listing recordings

    Returns:
        Dict containing the list of recordings
    """
    try:
        # Initialize Zoom auth from environment variables
        zoom_auth = ZoomAuth.from_env()

        # Get the access token
        access_token = zoom_auth.get_access_token()

        # Set default date range if not provided (last 30 days)
        if not params.from_date:
            from_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        else:
            from_date = params.from_date

        if not params.to_date:
            to_date = datetime.now().strftime("%Y-%m-%d")
        else:
            to_date = params.to_date

        # If user_id is provided, get recordings for that user
        if params.user_id:
            api_url = f"https://api.zoom.us/v2/users/{params.user_id}/recordings"
            query_params = {
                "from": from_date,
                "to": to_date,
                "page_size": params.page_size
            }

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(api_url, headers=headers, params=query_params)

                if response.status_code != 200:
                    error_message = f"Failed to list recordings: {response.status_code} - {response.text}"
                    logger.error(error_message)
                    raise Exception(error_message)

                return response.json()
        else:
            # Get all users' recordings
            users_url = "https://api.zoom.us/v2/users"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            import httpx
            all_recordings = []

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

                # Get recordings for each user
                for user in users_data.get("users", []):
                    user_id = user.get("id")
                    recordings_url = f"https://api.zoom.us/v2/users/{user_id}/recordings"

                    recordings_response = await client.get(
                        recordings_url,
                        headers=headers,
                        params={
                            "from": from_date,
                            "to": to_date,
                            "page_size": params.page_size
                        }
                    )

                    if recordings_response.status_code == 200:
                        recordings_data = recordings_response.json()
                        meetings = recordings_data.get("meetings", [])
                        # Add user info to each recording
                        for meeting in meetings:
                            meeting["user_email"] = user.get("email")
                            meeting["user_name"] = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
                        all_recordings.extend(meetings)

                return {
                    "from": from_date,
                    "to": to_date,
                    "total_recordings": len(all_recordings),
                    "meetings": all_recordings
                }

    except Exception as e:
        logger.error(f"Error listing recordings: {str(e)}")
        raise 