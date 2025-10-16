"""
Zoom MCP Contacts Tools

Tools for managing Zoom contacts and contact lists.
"""

import httpx
from pydantic import BaseModel, Field
from typing import Optional

from zoom_mcp.auth.zoom_auth import ZoomAuth


class ListContactsParams(BaseModel):
    """Parameters for listing Zoom contacts."""

    type: Optional[str] = Field(
        default=None,
        description="Contact type: 'company' for company directory contacts"
    )
    page_size: Optional[int] = Field(
        default=50,
        description="Number of contacts per page (max 50)"
    )
    next_page_token: Optional[str] = Field(
        default=None,
        description="Token for pagination"
    )


class GetContactParams(BaseModel):
    """Parameters for getting a specific contact."""

    contact_id: str = Field(
        description="The contact ID or email address"
    )


async def list_contacts(params: ListContactsParams) -> dict:
    """
    List Zoom contacts for the authenticated user.

    Args:
        params: Parameters for listing contacts

    Returns:
        Dictionary containing contact list data
    """
    zoom_auth = ZoomAuth.from_env()
    access_token = zoom_auth.get_access_token()

    # Try the general contacts endpoint (not team chat specific)
    api_url = "https://api.zoom.us/v2/contacts"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    query_params = {}
    if params.type:
        query_params["type"] = params.type
    if params.page_size:
        query_params["page_size"] = params.page_size
    if params.next_page_token:
        query_params["next_page_token"] = params.next_page_token

    async with httpx.AsyncClient() as client:
        response = await client.get(
            api_url,
            headers=headers,
            params=query_params
        )

        if response.status_code != 200:
            return {
                "error": f"Failed to list contacts: {response.status_code}",
                "message": response.text
            }

        return response.json()


async def get_contact(params: GetContactParams) -> dict:
    """
    Get details for a specific Zoom contact.

    Args:
        params: Parameters for getting contact details

    Returns:
        Dictionary containing contact details
    """
    zoom_auth = ZoomAuth.from_env()
    access_token = zoom_auth.get_access_token()

    # Try the general contacts endpoint (not team chat specific)
    api_url = f"https://api.zoom.us/v2/contacts/{params.contact_id}"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(api_url, headers=headers)

        if response.status_code != 200:
            return {
                "error": f"Failed to get contact: {response.status_code}",
                "message": response.text
            }

        return response.json()


async def search_contacts(query: str) -> dict:
    """
    Search Zoom contacts by name or email.

    Args:
        query: Search query string

    Returns:
        Dictionary containing matching contacts
    """
    zoom_auth = ZoomAuth.from_env()
    access_token = zoom_auth.get_access_token()

    api_url = "https://api.zoom.us/v2/contacts"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    params = {
        "search_key": query,
        "query_presence_status": True
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            api_url,
            headers=headers,
            params=params
        )

        if response.status_code != 200:
            return {
                "error": f"Failed to search contacts: {response.status_code}",
                "message": response.text
            }

        return response.json()
