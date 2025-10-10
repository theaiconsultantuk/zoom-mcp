# Using Zoom MCP Server with Gumloop

Since Gumloop cannot connect to custom MCP servers directly, we've added REST API endpoints that Gumloop's Python nodes can call.

---

## Server Endpoints

Your server now runs **TWO** services:

1. **MCP SSE Server** (port 3000): `https://zoom-mcp.theaiconsultant.co.uk/sse`
   - For MCP protocol clients (not Gumloop)

2. **REST API** (port 3001): `https://zoom-mcp.theaiconsultant.co.uk:3001/api/`
   - **Use this from Gumloop Python nodes!**

---

## Available REST Endpoints

### 1. Get Meetings for a Specific Date

**Endpoint:**
```
GET https://zoom-mcp.theaiconsultant.co.uk:3001/api/meetings/today?date=2025-10-15
```

**Response:**
```json
{
  "date": "2025-10-15",
  "total_meetings": 3,
  "meetings": [
    {
      "id": "123456789",
      "topic": "Team Standup",
      "start_time": "2025-10-15T09:00:00Z",
      "duration": 30,
      "user_email": "you@example.com",
      "user_name": "Your Name",
      "join_url": "https://zoom.us/j/123456789",
      "agenda": "",
      "type": 2
    }
  ]
}
```

### 2. Get Specific Meeting Details

**Endpoint:**
```
GET https://zoom-mcp.theaiconsultant.co.uk:3001/api/meetings/{meeting_id}
```

**Example:**
```
GET https://zoom-mcp.theaiconsultant.co.uk:3001/api/meetings/123456789
```

### 3. List All Users

**Endpoint:**
```
GET https://zoom-mcp.theaiconsultant.co.uk:3001/api/users
```

### 4. Get Recordings

**Endpoint:**
```
GET https://zoom-mcp.theaiconsultant.co.uk:3001/api/recordings?from_date=2025-10-01&to_date=2025-10-15
```

---

## Gumloop Python Node Example

**For getting meetings on October 15th:**

```python
import requests
import json

# Get meetings for October 15th
url = "https://zoom-mcp.theaiconsultant.co.uk:3001/api/meetings/today"
params = {"date": "2025-10-15"}

response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()

    print(f"Total meetings: {data['total_meetings']}")

    # Extract attendee emails from each meeting
    for meeting in data['meetings']:
        print(f"\nMeeting: {meeting['topic']}")
        print(f"Start: {meeting['start_time']}")
        print(f"Host: {meeting['user_email']}")
        print(f"Duration: {meeting['duration']} minutes")

        # To get participant data, you'd need to call get_meeting with the meeting_id
        # Zoom API doesn't return participants in the list endpoint

    output = data  # Return full data structure
else:
    print(f"Error: {response.status_code}")
    output = {"error": response.text}
```

**Note:** The Zoom API list meetings endpoint **does NOT include participant/attendee data**. To get participants:

1. List meetings to get meeting IDs
2. Call the `/api/meetings/{meeting_id}` endpoint for each meeting
3. The detailed endpoint includes `participant` data (if available)

Alternatively, use the Recordings API to get recordings which include participant lists.

---

## Coolify Configuration

After deployment, you'll need to add port 3001 to Coolify:

1. Go to **Configuration** → **General**
2. Update **Ports Exposes:** `3000,3001`
3. Update **Ports Mappings:** `3000:3000,3001:3001`
4. Save and redeploy

---

## Testing the REST API

```bash
# Test health check
curl https://zoom-mcp.theaiconsultant.co.uk:3001/health

# Get meetings for Oct 15th
curl "https://zoom-mcp.theaiconsultant.co.uk:3001/api/meetings/today?date=2025-10-15"

# Get all users
curl https://zoom-mcp.theaiconsultant.co.uk:3001/api/users
```

---

## Full Python Node Template

```python
import requests
from datetime import datetime

def get_zoom_meetings(date_str):
    """
    Get Zoom meetings for a specific date.

    Args:
        date_str: Date in YYYY-MM-DD format (e.g., "2025-10-15")

    Returns:
        List of meetings with details
    """
    url = "https://zoom-mcp.theaiconsultant.co.uk:3001/api/meetings/today"
    params = {"date": date_str}

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()

        # Extract relevant fields
        meetings_list = []
        for meeting in data.get('meetings', []):
            meetings_list.append({
                'id': meeting.get('id'),
                'topic': meeting.get('topic'),
                'start_time': meeting.get('start_time'),
                'duration': meeting.get('duration'),
                'host_email': meeting.get('user_email'),
                'host_name': meeting.get('user_name'),
                'join_url': meeting.get('join_url')
            })

        return {
            'date': date_str,
            'total': len(meetings_list),
            'meetings': meetings_list
        }

    except requests.exceptions.RequestException as e:
        return {
            'error': str(e),
            'date': date_str
        }

# Example usage
result = get_zoom_meetings("2025-10-15")
print(result)
```

---

## Important Notes

1. **Participants/Attendees:** The Zoom API doesn't provide participant lists in the meetings list endpoint. You need to:
   - Use the Recordings API (includes participant reports)
   - Or use Zoom Webhooks to track who joined meetings in real-time

2. **Rate Limits:** Zoom API has rate limits. For production use, implement:
   - Caching
   - Rate limiting
   - Error handling

3. **Authentication:** The server uses your Zoom credentials (already configured in environment variables)

---

**Last Updated:** October 10, 2025
