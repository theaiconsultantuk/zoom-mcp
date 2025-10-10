"""Zoom authentication module for MCP server.

This module handles Zoom OAuth 2.0 Server-to-Server authentication.
"""

import base64
import os
import json
from datetime import datetime, timedelta
from typing import Optional, List

import httpx


class ZoomAuth:
    """Handles Zoom OAuth 2.0 Server-to-Server authentication."""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        account_id: Optional[str] = None
    ):
        """Initialize Zoom authentication.

        Args:
            api_key: Zoom API Key (Client ID)
            api_secret: Zoom API Secret (Client Secret)
            account_id: Optional Zoom Account ID for JWT token
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.account_id = account_id
        self._token = None
        self._token_expiry = None

    def get_access_token(self) -> str:
        """Get a valid access token, generating a new one if necessary.

        Returns:
            str: The access token
        """
        if self._is_token_valid():
            return self._token

        return self._generate_token()

    def _is_token_valid(self) -> bool:
        """Check if the current token is still valid.

        Returns:
            bool: True if token is valid, False otherwise
        """
        if not self._token or not self._token_expiry:
            return False
        # Add 5 minute buffer before expiry
        return datetime.now() < (self._token_expiry - timedelta(minutes=5))

    def _generate_token(self) -> str:
        """Generate a new access token using OAuth2.

        Returns:
            str: The access token

        Raises:
            Exception: If token generation fails
        """
        # Create base64 encoded credentials
        credentials = base64.b64encode(
            f"{self.api_key}:{self.api_secret}".encode()
        ).decode()

        # Print debug information (with credentials masked)
        print(f"API Key: {'*' * len(self.api_key)}")
        print(f"API Secret: {'*' * len(self.api_secret)}")
        print(f"Account ID: {self.account_id}")

        # For Server-to-Server OAuth, scopes are pre-configured in the app
        # We don't need to request them in the token call
        with httpx.Client() as client:
            # Make the request with account_credentials grant type for Server-to-Server OAuth
            response = client.post(
                f"https://zoom.us/oauth/token?grant_type=account_credentials&account_id={self.account_id}",
                headers={
                    "Authorization": f"Basic {credentials}",
                },
                timeout=10.0,
            )

            print(f"Response status: {response.status_code}")
            
            if response.status_code != 200:
                error_message = f"Failed to get OAuth token: {response.status_code} - {response.text}"
                raise Exception(error_message)
                
            data = response.json()

        # Store token and expiry
        self._token = data["access_token"]
        self._token_expiry = datetime.now() + timedelta(seconds=data["expires_in"])

        return self._token

    @classmethod
    def from_env(cls) -> "ZoomAuth":
        """Create a ZoomAuth instance from environment variables.

        Returns:
            ZoomAuth: Configured ZoomAuth instance

        Raises:
            ValueError: If required environment variables are not set
        """
        api_key = os.getenv("ZOOM_API_KEY")
        api_secret = os.getenv("ZOOM_API_SECRET")
        account_id = os.getenv("ZOOM_ACCOUNT_ID")

        if not api_key or not api_secret:
            raise ValueError(
                "ZOOM_API_KEY and ZOOM_API_SECRET environment variables must be set"
            )
            
        if not account_id:
            raise ValueError(
                "ZOOM_ACCOUNT_ID environment variable must be set"
            )

        return cls(api_key=api_key, api_secret=api_secret, account_id=account_id) 