# Starting and Using the Zoom MCP Server

A comprehensive step-by-step guide for running and using the Zoom MCP server to gather data from your Zoom account.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Manual Server Startup](#manual-server-startup)
4. [Using with Claude Desktop](#using-with-claude-desktop)
5. [Standalone Usage](#standalone-usage)
6. [Example Queries](#example-queries)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- ✅ Python 3.11 or higher
- ✅ uv package manager
- ✅ Claude Desktop (for integrated usage)

### Required Credentials
- ✅ Zoom Server-to-Server OAuth App credentials
  - Client ID (API Key)
  - Client Secret (API Secret)
  - Account ID

### Environment Setup
Ensure your `.env` file exists at:
```
/Volumes/Courses/Scripts/Python/MCP/zoom-mcp/.env
```

With contents:
```env
ZOOM_API_KEY=your-client-id
ZOOM_API_SECRET=your-client-secret
ZOOM_ACCOUNT_ID=your-account-id
```

---

## Quick Start

### Option 1: Using with Claude Desktop (Recommended)

**Step 1:** Restart Claude Desktop
```bash
# Close Claude Desktop completely, then reopen it
```

**Step 2:** Verify Connection
- Open Claude Desktop
- Look for the Zoom server in the MCP servers list
- Should show "connected" status

**Step 3:** Start Using
Simply ask Claude questions like:
- "What meetings do I have today?"
- "List my recent Zoom recordings"
- "Show me all users in my account"

---

## Manual Server Startup

### Method 1: Using Virtual Environment

**Step 1:** Navigate to Project Directory
```bash
cd /Volumes/Courses/Scripts/Python/MCP/zoom-mcp
```

**Step 2:** Activate Virtual Environment
```bash
source .venv/bin/activate
```

**Step 3:** Start the Server
```bash
python -m zoom_mcp.server
```

**Expected Output:**
```
2025-10-10 02:33:02,035 - zoom_mcp.resources.recordings - INFO - RecordingResource initialized with auth manager
2025-10-10 02:33:02,046 - zoom_mcp.resources.recordings - INFO - RecordingResource initialized with auth manager
[Server is now running and waiting for connections]
```

### Method 2: Using uv (Recommended)

**Step 1:** Navigate to Project Directory
```bash
cd /Volumes/Courses/Scripts/Python/MCP/zoom-mcp
```

**Step 2:** Run with uv
```bash
uv run python -m zoom_mcp.server
```

This automatically handles the virtual environment for you.

---

## Using with Claude Desktop

### Initial Setup (One-Time)

**Step 1:** Verify Configuration File
```bash
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

Look for the `zoom` entry. It should look like:
```json
{
  "mcpServers": {
    "zoom": {
      "command": "/Users/paulcowen/.local/bin/uv",
      "args": [
        "--directory",
        "/Volumes/Courses/Scripts/Python/MCP/zoom-mcp",
        "run",
        "python",
        "-m",
        "zoom_mcp.server"
      ],
      "env": {
        "PATH": "/Users/paulcowen/.local/bin:/usr/local/bin:/usr/bin:/bin",
        "ZOOM_API_KEY": "your-api-key",
        "ZOOM_API_SECRET": "your-api-secret",
        "ZOOM_ACCOUNT_ID": "your-account-id"
      }
    }
  }
}
```

**Step 2:** Restart Claude Desktop
- Completely quit Claude Desktop
- Reopen Claude Desktop
- Wait for all MCP servers to connect

### Daily Usage

**Step 1:** Open Claude Desktop
The Zoom MCP server will automatically start and connect.

**Step 2:** Verify Connection
Look for the Zoom server indicator in the Claude Desktop interface.

**Step 3:** Ask Questions
Start asking Zoom-related questions naturally.

---

## Standalone Usage

### Testing Connection

**Test 1: Verify Environment Variables**
```bash
cd /Volumes/Courses/Scripts/Python/MCP/zoom-mcp
source .venv/bin/activate
python scripts/check_env.py
```

**Expected Output:**
```
🔍 Checking Environment Variables...

ZOOM_API_KEY: WRv5JXlFSXSZ5jmGtvznw
ZOOM_API_SECRET: ********************************
ZOOM_ACCOUNT_ID: mk8MCWYUT2-Er1nzO4LkAg

✅ All required environment variables are set.
```

**Test 2: Test Zoom API Connection**
```bash
python scripts/test_zoom_connection.py
```

**Expected Output:**
```
Running Zoom API connection tests at 2025-10-10 02:22:05

===== Testing OAuth Token Generation =====
✅ Successfully generated OAuth token: eyJzdiI6Ij...xS2BAC86rQ

===== Testing Account Access =====
✅ Successfully accessed account. Found 1 users.

===== Testing Recordings Access =====
✅ Successfully accessed recordings. Found 5 recordings.
```

### Gathering Specific Data

#### Get Today's Meetings

**Using Python Script:**
```python
import asyncio
from zoom_mcp.tools.meetings import list_todays_meetings, ListTodaysMeetingsParams

async def get_todays_meetings():
    params = ListTodaysMeetingsParams()
    meetings = await list_todays_meetings(params)
    print(meetings)

asyncio.run(get_todays_meetings())
```

#### List Recent Recordings

**Using Python Script:**
```python
import asyncio
from zoom_mcp.tools.recordings import list_recordings, ListRecordingsParams

async def get_recent_recordings():
    params = ListRecordingsParams(
        from_date="2025-09-01",
        to_date="2025-10-10"
    )
    recordings = await list_recordings(params)
    print(recordings)

asyncio.run(get_recent_recordings())
```

#### List All Users

**Using Python Script:**
```python
import asyncio
from zoom_mcp.tools.users import list_users, ListUsersParams

async def get_all_users():
    params = ListUsersParams(status="active")
    users = await list_users(params)
    print(users)

asyncio.run(get_all_users())
```

---

## Example Queries

### Using Claude Desktop

#### Meeting Queries

**"What meetings do I have today?"**
- Uses: `list_todays_meetings`
- Returns: All meetings scheduled for today

**"Show me all my scheduled meetings for next week"**
- Uses: `list_meetings` with date range
- Returns: Meetings scheduled for the specified period

**"Give me details about meeting ID 12345678"**
- Uses: `get_meeting`
- Returns: Complete meeting information

#### Recording Queries

**"List my Zoom recordings from the last 7 days"**
- Uses: `list_recordings` with date range
- Returns: Recordings from the past week

**"Find all recordings from user@example.com"**
- Uses: `list_recordings` with user_id filter
- Returns: User-specific recordings

**"Get the transcript for this recording: https://zoom.us/rec/share/abc123"**
- Uses: `get_recording_transcript`
- Returns: Full transcript with speaker labels

#### User Queries

**"Who are all the users in my Zoom account?"**
- Uses: `list_users`
- Returns: List of all active users

**"Get details for user john@example.com"**
- Uses: `get_user`
- Returns: Complete user profile

---

## Troubleshooting

### Server Won't Start

**Problem:** Server disconnects immediately

**Solution:**
1. Check the logs:
```bash
tail -f ~/Library/Logs/Claude/mcp-server-zoom.log
```

2. Look for error messages like:
```
error: Failed to spawn: `zoom_mcp.server`
```

3. Verify configuration includes `python -m`:
```json
"args": ["--directory", "/path/to/zoom-mcp", "run", "python", "-m", "zoom_mcp.server"]
```

### Authentication Errors

**Problem:** Getting 401 Unauthorized errors

**Solutions:**

1. **Verify credentials in .env file:**
```bash
cat /Volumes/Courses/Scripts/Python/MCP/zoom-mcp/.env
```

2. **Check Zoom app is activated:**
- Go to https://marketplace.zoom.us/
- Navigate to your app
- Ensure it's activated

3. **Verify scopes are enabled:**
- Check that all required scopes are added
- Deactivate and reactivate the app

### No Tools Available

**Problem:** Claude Desktop shows server connected but no tools

**Solutions:**

1. **Restart Claude Desktop completely**

2. **Check server logs for initialization:**
```bash
grep "RecordingResource initialized" ~/Library/Logs/Claude/mcp-server-zoom.log
```

3. **Verify tools are registered:**
```bash
cd /Volumes/Courses/Scripts/Python/MCP/zoom-mcp
source .venv/bin/activate
python -c "from zoom_mcp.server import create_zoom_mcp; s = create_zoom_mcp(); print('Server created successfully')"
```

### Rate Limiting

**Problem:** Getting rate limit errors

**Solution:**
- Zoom has API rate limits (varies by plan)
- Reduce the frequency of requests
- Use pagination with smaller page sizes
- Implement retry logic with exponential backoff

### Connection Timeouts

**Problem:** Requests timing out

**Solutions:**

1. **Check network connectivity:**
```bash
curl -I https://api.zoom.us
```

2. **Verify Zoom service status:**
Visit https://status.zoom.us/

3. **Increase timeout in code if needed:**
```python
async with httpx.AsyncClient(timeout=30.0) as client:
    # Your code here
```

---

## Advanced Usage

### Running in Background

**Using nohup:**
```bash
cd /Volumes/Courses/Scripts/Python/MCP/zoom-mcp
nohup uv run python -m zoom_mcp.server > server.log 2>&1 &
```

**Using screen:**
```bash
screen -S zoom-mcp
cd /Volumes/Courses/Scripts/Python/MCP/zoom-mcp
uv run python -m zoom_mcp.server
# Press Ctrl+A, then D to detach
```

**Reattach to screen:**
```bash
screen -r zoom-mcp
```

### Custom Scripts

Create custom scripts in the `scripts/` directory for specific data gathering tasks.

**Example: Daily Meeting Report**
```python
#!/usr/bin/env python3
"""Generate daily meeting report."""

import asyncio
import json
from datetime import datetime
from zoom_mcp.tools.meetings import list_todays_meetings, ListTodaysMeetingsParams

async def generate_daily_report():
    params = ListTodaysMeetingsParams()
    meetings = await list_todays_meetings(params)

    report = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "total_meetings": meetings.get("total_meetings", 0),
        "meetings": meetings.get("meetings", [])
    }

    # Save to file
    with open(f"meeting_report_{report['date']}.json", "w") as f:
        json.dump(report, f, indent=2)

    print(f"Report generated: meeting_report_{report['date']}.json")

if __name__ == "__main__":
    asyncio.run(generate_daily_report())
```

**Run it:**
```bash
cd /Volumes/Courses/Scripts/Python/MCP/zoom-mcp
source .venv/bin/activate
python scripts/daily_meeting_report.py
```

---

## Best Practices

### 1. Always Check Connection First
```bash
python scripts/test_zoom_connection.py
```

### 2. Use Date Filters for Large Datasets
```python
# Good - specific date range
params = ListRecordingsParams(
    from_date="2025-10-01",
    to_date="2025-10-10"
)

# Avoid - might return too much data
params = ListRecordingsParams()  # Defaults to last 30 days
```

### 3. Implement Error Handling
```python
try:
    meetings = await list_meetings(params)
except Exception as e:
    logger.error(f"Failed to get meetings: {e}")
    # Handle error appropriately
```

### 4. Use Pagination for Large Results
```python
params = ListUsersParams(page_size=100)  # Max 300
# Process in batches
```

### 5. Monitor Rate Limits
Keep track of API calls to avoid hitting rate limits.

---

## Quick Reference

### Server Locations
- **Project Directory:** `/Volumes/Courses/Scripts/Python/MCP/zoom-mcp`
- **Virtual Environment:** `/Volumes/Courses/Scripts/Python/MCP/zoom-mcp/.venv`
- **Configuration:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Logs:** `~/Library/Logs/Claude/mcp-server-zoom.log`

### Common Commands
```bash
# Start server manually
cd /Volumes/Courses/Scripts/Python/MCP/zoom-mcp
uv run python -m zoom_mcp.server

# Test connection
python scripts/test_zoom_connection.py

# Check environment
python scripts/check_env.py

# View logs
tail -f ~/Library/Logs/Claude/mcp-server-zoom.log
```

### Available Tools
1. `list_todays_meetings` - Today's meetings
2. `list_meetings` - All meetings with filters
3. `get_meeting` - Specific meeting details
4. `list_recordings` - Cloud recordings
5. `get_recording_transcript` - Recording transcripts
6. `list_users` - Account users
7. `get_user` - Specific user details

---

## Support

For issues or questions:
1. Check the logs: `~/Library/Logs/Claude/mcp-server-zoom.log`
2. Review troubleshooting section above
3. Test connection with: `python scripts/test_zoom_connection.py`
4. Verify Zoom app configuration at https://marketplace.zoom.us/

---

**Last Updated:** October 10, 2025
