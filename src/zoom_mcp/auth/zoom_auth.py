"""Zoom authentication module for MCP server.

This module handles Zoom OAuth 2.0 Server-to-Server authentication.
"""

import os
from datetime import datetime, timedelta
from typing import Optional

import jwt


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
        return datetime.now() < self._token_expiry

    def _generate_token(self) -> str:
        """Generate a new JWT token.

        Returns:
            str: The generated JWT token
        """
        # Token expires in 1 hour
        expiry = datetime.now() + timedelta(hours=1)
        
        # Prepare the payload
        payload = {
            "iss": self.api_key,
            "exp": int(expiry.timestamp()),
        }
        
        if self.account_id:
            payload["account_id"] = self.account_id

        # Generate the token
        self._token = jwt.encode(
            payload,
            self.api_secret,
            algorithm="HS256"
        )
        self._token_expiry = expiry

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

        return cls(api_key=api_key, api_secret=api_secret, account_id=account_id) 