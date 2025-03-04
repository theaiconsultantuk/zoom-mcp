#!/usr/bin/env python3
"""Script to guide users through setting up Zoom API authentication."""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Confirm, Prompt

app = typer.Typer()
console = Console()


def get_env_file_path() -> Path:
    """Get the path to the .env file."""
    return Path.cwd() / ".env"


def check_env_file() -> bool:
    """Check if .env file exists and has Zoom credentials."""
    env_path = get_env_file_path()
    if not env_path.exists():
        return False

    with open(env_path) as f:
        content = f.read()
        return all(
            key in content
            for key in ["ZOOM_API_KEY", "ZOOM_API_SECRET", "ZOOM_ACCOUNT_ID"]
        )


def create_env_file(api_key: str, api_secret: str, account_id: str) -> None:
    """Create or update the .env file with Zoom credentials."""
    env_path = get_env_file_path()
    env_content = [
        "# Zoom API Credentials",
        f"ZOOM_API_KEY={api_key}",
        f"ZOOM_API_SECRET={api_secret}",
        f"ZOOM_ACCOUNT_ID={account_id}",
    ]

    with open(env_path, "w") as f:
        f.write("\n".join(env_content) + "\n")


@app.command()
def setup(
    api_key: Optional[str] = typer.Option(
        None, help="Zoom API Key (Client ID)"
    ),
    api_secret: Optional[str] = typer.Option(
        None, help="Zoom API Secret (Client Secret)"
    ),
    account_id: Optional[str] = typer.Option(
        None, help="Zoom Account ID (required for Server-to-Server OAuth)"
    ),
) -> None:
    """Set up Zoom API authentication credentials."""
    console.print(
        Markdown(
            """
# Zoom API Authentication Setup

This script will help you set up your Zoom API credentials for the MCP server.

## Prerequisites

1. A Zoom Developer account (https://marketplace.zoom.us/develop/create)
2. A Server-to-Server OAuth app created in the Zoom Marketplace
3. The following credentials from your Zoom app:
   - API Key (Client ID)
   - API Secret (Client Secret)
   - Account ID (required for Server-to-Server OAuth)

## Instructions

1. Go to the [Zoom Marketplace](https://marketplace.zoom.us/develop/create)
2. Click "Create App"
3. Choose "Server-to-Server OAuth" as the app type
4. Fill in the app information:
   - App Name: "Zoom MCP Server" (or your preferred name)
   - App Type: Server-to-Server OAuth
   - User Type: Account
5. After creating the app, you'll find:
   - API Key (Client ID) in the app's credentials
   - API Secret (Client Secret) in the app's credentials
   - Account ID in your Zoom account settings

## Security Note

Your credentials will be stored in a `.env` file in your project directory.
Make sure to:
- Never commit this file to version control
- Keep your credentials secure
- Rotate credentials if they are compromised
"""
        )
    )

    if check_env_file():
        if not Confirm.ask(
            "Zoom credentials are already configured. Do you want to update them?"
        ):
            return

    # Get credentials from command line or prompt
    if not api_key:
        api_key = Prompt.ask("Enter your Zoom API Key (Client ID)")
    if not api_secret:
        api_secret = Prompt.ask("Enter your Zoom API Secret (Client Secret)")
    if not account_id:
        account_id = Prompt.ask(
            "Enter your Zoom Account ID (required for Server-to-Server OAuth)"
        )

    # Validate credentials
    if not api_key or not api_secret or not account_id:
        console.print("[red]Error: All credentials are required[/red]")
        sys.exit(1)

    # Create or update .env file
    create_env_file(
        api_key=api_key,
        api_secret=api_secret,
        account_id=account_id,
    )

    console.print(
        "\n[green]Success! Zoom credentials have been configured.[/green]\n"
        "You can now use the MCP server with your Zoom API credentials."
    )


if __name__ == "__main__":
    app() 