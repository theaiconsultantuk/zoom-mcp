#!/usr/bin/env python3
"""
Check Environment Variables

This script checks if the required environment variables for the Zoom MCP server
are set correctly.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Required environment variables
required_vars = [
    "ZOOM_API_KEY",
    "ZOOM_API_SECRET",
    "ZOOM_ACCOUNT_ID",
]

# Check if all required variables are set
missing_vars = []
for var in required_vars:
    if not os.getenv(var):
        missing_vars.append(var)

# Print results
if missing_vars:
    print("❌ The following required environment variables are missing:")
    for var in missing_vars:
        print(f"  - {var}")
    print("\nPlease set these variables in your .env file or environment.")
    sys.exit(1)
else:
    print("✅ All required environment variables are set.")
    
    # Print the values (masked for secrets)
    print("\nEnvironment variables:")
    print(f"  - ZOOM_API_KEY: {'*' * 8}{os.getenv('ZOOM_API_KEY')[-4:]}")
    print(f"  - ZOOM_API_SECRET: {'*' * 8}{os.getenv('ZOOM_API_SECRET')[-4:]}")
    print(f"  - ZOOM_ACCOUNT_ID: {os.getenv('ZOOM_ACCOUNT_ID')}")
    
    print("\nYou can now run the Zoom MCP server.")
    sys.exit(0) 