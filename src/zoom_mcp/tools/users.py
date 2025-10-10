"""
Zoom Users Tools

This module provides tools for working with Zoom users.
"""

import logging
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from zoom_mcp.auth.zoom_auth import ZoomAuth

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class ListUsersParams(BaseModel):
    """Parameters for listing users."""
    status: str = Field("active", description="User status: active, inactive, or pending")
    page_size: int = Field(30, description="Number of records per page (max 300)")
    role_id: Optional[str] = Field(None, description="Filter by role ID")


class GetUserParams(BaseModel):
    """Parameters for getting user details."""
    user_id: str = Field(..., description="User ID or email address")


async def list_users(params: ListUsersParams) -> Dict[str, Any]:
    """
    List Zoom users in the account.

    Args:
        params: Parameters for listing users

    Returns:
        Dict containing the list of users
    """
    try:
        # Initialize Zoom auth from environment variables
        zoom_auth = ZoomAuth.from_env()

        # Get the access token
        access_token = zoom_auth.get_access_token()

        # Construct the API URL
        api_url = "https://api.zoom.us/v2/users"

        # Build query parameters
        query_params = {
            "status": params.status,
            "page_size": params.page_size
        }

        if params.role_id:
            query_params["role_id"] = params.role_id

        # Make the API request
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, headers=headers, params=query_params)

            if response.status_code != 200:
                error_message = f"Failed to list users: {response.status_code} - {response.text}"
                logger.error(error_message)
                raise Exception(error_message)

            return response.json()

    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        raise


async def get_user(params: GetUserParams) -> Dict[str, Any]:
    """
    Get details for a specific user.

    Args:
        params: Parameters for getting user details

    Returns:
        Dict containing user details
    """
    try:
        # Initialize Zoom auth from environment variables
        zoom_auth = ZoomAuth.from_env()

        # Get the access token
        access_token = zoom_auth.get_access_token()

        # Construct the API URL
        api_url = f"https://api.zoom.us/v2/users/{params.user_id}"

        # Make the API request
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, headers=headers)

            if response.status_code != 200:
                error_message = f"Failed to get user: {response.status_code} - {response.text}"
                logger.error(error_message)
                raise Exception(error_message)

            return response.json()

    except Exception as e:
        logger.error(f"Error getting user: {str(e)}")
        raise
