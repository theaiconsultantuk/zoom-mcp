#!/usr/bin/env python3
"""Script to test Zoom API connection and authentication."""

import json
import sys
from pathlib import Path

import httpx
import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from zoom_mcp.auth.zoom_auth import ZoomAuth

app = typer.Typer()
console = Console()

# Zoom API base URL
ZOOM_API_BASE = "https://api.zoom.us/v2"


def check_env_file() -> bool:
    """Check if .env file exists and has Zoom credentials."""
    env_path = Path.cwd() / ".env"
    if not env_path.exists():
        return False

    with open(env_path) as f:
        content = f.read()
        return all(
            key in content
            for key in ["ZOOM_API_KEY", "ZOOM_API_SECRET", "ZOOM_ACCOUNT_ID"]
        )


@app.command()
def test() -> None:
    """Test Zoom API connection and authentication."""
    if not check_env_file():
        console.print(
            Panel(
                "[red]Error: Zoom credentials not found.[/red]\n"
                "Please run `python scripts/setup_zoom_auth.py` first.\n"
                "Make sure to include ZOOM_ACCOUNT_ID in your .env file.",
                title="Configuration Error",
            )
        )
        sys.exit(1)

    try:
        # Load environment variables from .env file
        load_dotenv()
        
        # Initialize Zoom authentication
        auth = ZoomAuth.from_env()
        
        # Get access token
        token = auth.get_access_token()
        
        # Test API connection
        with httpx.Client() as client:
            # Verify user access
            console.print("[blue]Testing /users/me endpoint...[/blue]")
            response = client.get(
                f"{ZOOM_API_BASE}/users/me",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                timeout=10.0,
            )
            
            # Print response details for debugging
            console.print(f"Status: {response.status_code}")
            if response.status_code != 200:
                console.print(f"Error: {response.text}")
                
            response.raise_for_status()
            user_data = response.json()
            console.print(f"[green]Successfully connected as {user_data.get('email')}[/green]")
        
        # Create results table
        table = Table(title="Zoom API Connection Test")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="yellow")
        
        # Add results
        table.add_row(
            "Environment Variables",
            "✓",
            "All required variables found",
        )
        table.add_row(
            "OAuth Token Generation",
            "✓",
            "Token generated successfully",
        )
        table.add_row(
            "User Access",
            "✓",
            f"Successfully connected as {user_data.get('email')}",
        )
        
        # Display results
        console.print(table)
        
        console.print(
            "\n[green]Success! Zoom API connection test passed.[/green]\n"
            "Your credentials are valid and ready to use."
        )
        
    except httpx.HTTPError as e:
        if e.response and e.response.status_code == 401:
            console.print(
                Panel(
                    "[red]Error: Authentication failed. Please check:\n"
                    "1. Your API Key and Secret are correct\n"
                    "2. Your app has the necessary scopes in Zoom Marketplace:\n"
                    "   - user:read:admin\n"
                    "3. Your app is activated in Zoom Marketplace[/red]",
                    title="Authentication Error",
                )
            )
        elif e.response and e.response.status_code == 400:
            error_text = e.response.text
            try:
                error_json = json.loads(error_text)
                error_message = error_json.get("message", "Unknown error")
                error_code = error_json.get("code", "Unknown code")
            except:
                error_message = error_text
                error_code = "Unknown"
                
            console.print(
                Panel(
                    f"[red]Error: Bad Request (Code: {error_code})\n"
                    f"Message: {error_message}\n\n"
                    "Please check:\n"
                    "1. Your app has the necessary permissions\n"
                    "2. Your account has the necessary privileges\n"
                    "3. The scopes are correctly configured in your app[/red]",
                    title="Configuration Error",
                )
            )
        elif e.response and e.response.status_code == 404:
            console.print(
                Panel(
                    "[red]Error: Resource not found. Please check:\n"
                    "1. The endpoint URL is correct\n"
                    "2. Your user has access to the requested resource[/red]",
                    title="Resource Error",
                )
            )
        else:
            console.print(
                Panel(
                    f"[red]Error: Failed to connect to Zoom API: {str(e)}[/red]\n"
                    f"Status Code: {e.response.status_code if e.response else 'Unknown'}\n"
                    f"Response: {e.response.text if e.response else 'No response'}\n"
                    "Please check your credentials and try again.",
                    title="API Connection Error",
                )
            )
        sys.exit(1)
    except Exception as e:
        console.print(
            Panel(
                f"[red]Error: {str(e)}[/red]\n"
                "Please check your credentials and try again.",
                title="Connection Error",
            )
        )
        sys.exit(1)


if __name__ == "__main__":
    app()