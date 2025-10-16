"""
Post-Meeting Automation

Generate meeting notes, download recordings, and create summaries.
"""

import httpx
from datetime import datetime
from typing import Optional, Dict, List

from zoom_mcp.auth.zoom_auth import ZoomAuth


async def get_meeting_recording_details(meeting_id: str) -> Optional[dict]:
    """
    Get recording details for a specific meeting.

    Args:
        meeting_id: Meeting ID or UUID

    Returns:
        Recording details if available
    """
    zoom_auth = ZoomAuth.from_env()
    access_token = zoom_auth.get_access_token()

    # Try to get recording
    api_url = f"https://api.zoom.us/v2/meetings/{meeting_id}/recordings"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(api_url, headers=headers)

        if response.status_code == 200:
            return response.json()

        return None


async def generate_meeting_notes(meeting_id: str) -> dict:
    """
    Generate comprehensive meeting notes including summary, transcript, and action items.

    Args:
        meeting_id: Meeting ID

    Returns:
        Complete meeting notes package
    """
    zoom_auth = ZoomAuth.from_env()
    access_token = zoom_auth.get_access_token()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    notes = {
        "meeting_id": meeting_id,
        "generated_at": datetime.now().isoformat(),
        "meeting_details": None,
        "ai_summary": None,
        "recording_details": None,
        "transcript": None,
        "action_items": []
    }

    async with httpx.AsyncClient() as client:
        # 1. Get meeting details
        meeting_response = await client.get(
            f"https://api.zoom.us/v2/meetings/{meeting_id}",
            headers=headers
        )
        if meeting_response.status_code == 200:
            notes["meeting_details"] = meeting_response.json()

        # 2. Get AI summary
        summary_response = await client.get(
            f"https://api.zoom.us/v2/meetings/{meeting_id}/meeting_summary",
            headers=headers
        )
        if summary_response.status_code == 200:
            summary_data = summary_response.json()
            notes["ai_summary"] = summary_data

            # Extract action items from summary
            if "next_steps" in summary_data:
                notes["action_items"] = summary_data["next_steps"]

        # 3. Get recording details
        recording_details = await get_meeting_recording_details(meeting_id)
        if recording_details:
            notes["recording_details"] = recording_details

            # Get transcript if available
            recording_files = recording_details.get("recording_files", [])
            for file in recording_files:
                if file.get("file_type") == "TRANSCRIPT":
                    transcript_url = file.get("download_url")
                    if transcript_url:
                        # Note: Actual transcript download requires additional processing
                        notes["transcript"] = {
                            "available": True,
                            "download_url": transcript_url
                        }

    return notes


async def download_recording(meeting_id: str, file_type: str = "MP4") -> dict:
    """
    Get download URLs for meeting recordings.

    Args:
        meeting_id: Meeting ID
        file_type: Type of file to download (MP4, M4A, TRANSCRIPT, etc.)

    Returns:
        Download URLs and file details
    """
    recording_details = await get_meeting_recording_details(meeting_id)

    if not recording_details:
        return {
            "error": "No recording found for this meeting",
            "meeting_id": meeting_id
        }

    recording_files = recording_details.get("recording_files", [])
    downloads = []

    for file in recording_files:
        if file_type == "ALL" or file.get("file_type") == file_type:
            downloads.append({
                "file_type": file.get("file_type"),
                "file_size": file.get("file_size"),
                "download_url": file.get("download_url"),
                "recording_start": file.get("recording_start"),
                "recording_end": file.get("recording_end")
            })

    return {
        "meeting_id": meeting_id,
        "total_files": len(downloads),
        "files": downloads
    }
