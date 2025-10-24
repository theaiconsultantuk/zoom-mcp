# Zoom MCP REST API Documentation

**Base URL:** `http://your-server:3001`
**Version:** 2.0.0

## Table of Contents

- [Authentication](#authentication)
- [Core Endpoints](#core-endpoints)
- [User Management](#user-management)
- [Meetings](#meetings)
- [Natural Language Features](#natural-language-features)
- [Contacts](#contacts)
- [Recordings](#recordings)
- [Post-Meeting Automation](#post-meeting-automation)
- [Error Handling](#error-handling)

---

## Authentication

All endpoints use Zoom Server-to-Server OAuth 2.0 authentication configured via environment variables. No API keys need to be passed in requests.

---

## Core Endpoints

### Get API Information
```http
GET /
```

**Response:**
```json
{
  "name": "Zoom MCP REST API",
  "version": "2.0.0",
  "endpoints": {
    "users": {...},
    "meetings": {...},
    "natural_language": {...},
    "contacts": {...},
    "post_meeting": {...},
    "recordings": {...}
  },
  "features": [...]
}
```

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-16T04:13:23.568391"
}
```

---

## User Management

### List All Users
```http
GET /api/users
```

**Response:**
```json
{
  "page_count": 1,
  "page_number": 1,
  "page_size": 30,
  "total_records": 1,
  "users": [
    {
      "id": "uyEC1mPzR1qkzaV-8-mycw",
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com",
      "type": 2,
      "timezone": "Europe/London",
      "status": "active"
    }
  ]
}
```

### Get Current User
```http
GET /api/users/me
```

**Response:**
```json
{
  "id": "uyEC1mPzR1qkzaV-8-mycw",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "pmi": 3926943772,
  "timezone": "Europe/London",
  "personal_meeting_url": "https://zoom.us/j/3926943772"
}
```

### Get Specific User
```http
GET /api/users/{user_id}
```

---

## Meetings

### List Today's Meetings
```http
GET /api/meetings/today
```

**Response:**
```json
{
  "date": "2025-10-16",
  "total_meetings": 5,
  "meetings": [
    {
      "id": 82329310172,
      "topic": "Team Standup",
      "type": 2,
      "start_time": "2025-10-16T10:00:00Z",
      "duration": 60,
      "join_url": "https://zoom.us/j/82329310172"
    }
  ]
}
```

### Get Meeting Templates
```http
GET /api/meetings/templates
```

**Response:**
```json
{
  "success": true,
  "templates": {
    "think_tank": {
      "topic": "Weekly Thinktank Meeting",
      "duration": 90,
      "agenda": "Weekly discussion"
    }
  }
}
```

### Create Meeting
```http
POST /api/meetings/create?topic={topic}&start_time={iso_time}&duration={minutes}
```

**Query Parameters:**
- `topic` (required): Meeting topic
- `start_time` (required): ISO 8601 format (e.g., `2025-10-17T10:00:00Z`)
- `duration` (optional): Duration in minutes (default: 60)
- `timezone` (optional): Timezone (default: Europe/London)
- `agenda` (optional): Meeting agenda

**Example:**
```bash
POST /api/meetings/create?topic=Team%20Sync&start_time=2025-10-17T10:00:00Z&duration=30
```

**Response:**
```json
{
  "success": true,
  "meeting_id": 87290589714,
  "join_url": "https://zoom.us/j/87290589714",
  "start_url": "https://zoom.us/s/87290589714?zak=...",
  "topic": "Team Sync",
  "start_time": "2025-10-17T10:00:00Z",
  "duration": 30
}
```

### Get Meeting Details
```http
GET /api/meetings/{meeting_id}
```

### Update Meeting
```http
PATCH /api/meetings/{meeting_id}
```

**Body (JSON):**
```json
{
  "topic": "Updated Meeting Title",
  "start_time": "2025-10-17T15:00:00Z",
  "duration": 45,
  "agenda": "Updated agenda"
}
```

### Delete Meeting
```http
DELETE /api/meetings/{meeting_id}
```

**Response:**
```json
{
  "success": true,
  "message": "Meeting deleted successfully",
  "meeting_id": "87290589714"
}
```

### Search Meetings
```http
GET /api/meetings/find/{description}
```

**Example:**
```bash
GET /api/meetings/find/Team
```

**Response:**
```json
{
  "query": "Team",
  "total_matches": 2,
  "meetings": [
    {
      "id": 82329310172,
      "topic": "Team Standup",
      "start_time": "2025-10-16T10:00:00Z"
    }
  ]
}
```

---

## Natural Language Features

### Book Meeting with Natural Language
```http
POST /api/meetings/book-natural?description={when}&topic={topic}&duration={duration}
```

**Query Parameters:**
- `description` (required): Natural language date/time (e.g., "tomorrow at 3pm", "next Friday morning")
- `topic` (optional): Meeting topic
- `duration` (optional): Duration as text (e.g., "1 hour", "45 minutes")
- `timezone` (optional): Timezone (default: Europe/London)
- `contact_name` (optional): Contact to invite

**Supported Formats:**
- Relative: "tomorrow", "next Friday", "in 2 hours"
- Time of day: "morning" (9am), "afternoon" (2pm), "evening" (6pm)
- Specific: "at 3pm", "at 10:30am"
- Combined: "tomorrow afternoon", "next Monday at 2pm"

**Examples:**
```bash
POST /api/meetings/book-natural?description=tomorrow%20at%203pm&topic=Strategy%20Review

POST /api/meetings/book-natural?description=next%20Friday%20morning&contact_name=Sarah&duration=1%20hour
```

**Response:**
```json
{
  "success": true,
  "meeting_id": 87420530060,
  "parsed_time": "2025-10-17T15:00:00Z",
  "join_url": "https://zoom.us/j/87420530060"
}
```

---

## Contacts

### List Contacts
```http
GET /api/contacts
```

### Search Personal Contacts
```http
GET /api/contacts/search/{query}
```

**Example:**
```bash
GET /api/contacts/search/Sarah
```

**Response:**
```json
{
  "query": "Sarah",
  "total_matches": 1,
  "contacts": [
    {
      "name": "Sarah Johnson",
      "email": "sarah@example.com",
      "phone": "+1234567890",
      "company": "Acme Corp"
    }
  ]
}
```

### Book Meeting with Contact
```http
POST /api/meetings/book-with-contact?contact_name={name}&description={when}&topic={topic}
```

**Query Parameters:**
- `contact_name` (required): Name from personal_contacts.csv
- `description` (required): Natural language date/time
- `topic` (optional): Meeting topic
- `duration` (optional): Duration text

**Example:**
```bash
POST /api/meetings/book-with-contact?contact_name=Sarah&description=Friday%20at%202pm&topic=Project%20Review
```

---

## Recordings

### List All Recordings
```http
GET /api/recordings
```

**Response:**
```json
{
  "from": "2025-09-16",
  "to": "2025-10-16",
  "total_recordings": 4,
  "meetings": [
    {
      "uuid": "+pafZ7aARQaE1PZTShAELQ==",
      "id": 87420530060,
      "topic": "Weekly Meeting",
      "start_time": "2025-10-02T17:52:06Z",
      "duration": 159,
      "recording_count": 5,
      "share_url": "https://zoom.us/rec/share/...",
      "recording_files": [
        {
          "file_type": "MP4",
          "file_size": 1281842048,
          "download_url": "https://zoom.us/rec/download/..."
        }
      ]
    }
  ]
}
```

---

## Post-Meeting Automation

### Get Meeting Notes
```http
GET /api/meetings/{meeting_id}/notes
```

**Response:**
```json
{
  "meeting_id": "87420530060",
  "generated_at": "2025-10-16T04:13:36.013591",
  "meeting_details": {
    "topic": "Weekly Meeting",
    "duration": 159,
    "participants": 12
  },
  "ai_summary": "Discussion focused on Q4 goals and project timelines...",
  "transcript": "Full meeting transcript text...",
  "action_items": [
    "Follow up with design team on mockups",
    "Schedule review meeting for next week"
  ],
  "recording_details": {
    "total_files": 5,
    "total_size": 1439416551
  }
}
```

### Get Recording Download Links
```http
GET /api/meetings/{meeting_id}/download
```

**Response:**
```json
{
  "meeting_id": "87420530060",
  "recording_files": [
    {
      "id": "9bd62c75-81fd-4e84-ae32-4e479443868e",
      "file_type": "MP4",
      "file_size": 1281842048,
      "download_url": "https://zoom.us/rec/download/..."
    },
    {
      "file_type": "TRANSCRIPT",
      "download_url": "https://zoom.us/rec/download/..."
    }
  ]
}
```

---

## Error Handling

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common HTTP Status Codes

- `200` - Success
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (authentication failed)
- `403` - Forbidden (insufficient scopes)
- `404` - Not Found (resource doesn't exist)
- `422` - Unprocessable Entity (validation error)
- `500` - Internal Server Error

### Example Error Responses

**Missing Required Parameter:**
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["query", "topic"],
      "msg": "Field required"
    }
  ]
}
```

**No Meeting Found:**
```json
{
  "detail": "No meeting found matching 'Team Sync'"
}
```

**Insufficient Scopes:**
```json
{
  "error": "Failed to list contacts: 400",
  "message": "Invalid access token, does not contain scopes:[contact:read:list_contacts]"
}
```

---

## Rate Limiting

Zoom API has rate limits:
- 10 requests per second (light)
- 40 requests per second (medium)
- 80 requests per second (heavy)

The API automatically handles rate limiting with exponential backoff.

---

## Testing

Use the comprehensive test script:

```bash
python3 scripts/test_all_endpoints.py
```

Or test individual endpoints:

```bash
# Get API info
curl http://localhost:3001/

# List users
curl http://localhost:3001/api/users

# Create meeting
curl -X POST "http://localhost:3001/api/meetings/create?topic=Test&start_time=2025-10-17T10:00:00Z"
```

---

## Support

- **Issues:** [GitHub Issues](https://github.com/theaiconsultantuk/zoom-mcp/issues)
- **Documentation:** See main README.md
- **Live API Docs:** Visit `http://your-server:3001/` when server is running
