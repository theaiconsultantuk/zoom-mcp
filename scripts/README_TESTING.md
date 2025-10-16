# Zoom MCP Comprehensive Testing

This directory contains comprehensive testing scripts for the Zoom MCP API.

## Quick Start

```bash
# Run all endpoint tests
python3 scripts/test_all_endpoints.py

# Or make it executable and run directly
chmod +x scripts/test_all_endpoints.py
./scripts/test_all_endpoints.py
```

## What Gets Tested

The comprehensive test script (`test_all_endpoints.py`) tests all Zoom MCP REST API endpoints:

### 1. Core Endpoints
- `GET /` - API root
- `GET /api` - API documentation

### 2. User Management
- `GET /api/users` - List all users
- `GET /api/users/me` - Current user details

### 3. Meeting Listing
- `GET /api/meetings` - List all meetings
- `GET /api/meetings/today` - Today's meetings
- `GET /api/meetings/upcoming` - Upcoming meetings

### 4. Meeting Creation
- `POST /api/meetings` - Create standard meeting

### 5. Natural Language Booking
- `POST /api/meetings/book-natural` - Create meeting with natural language
  - Example: "tomorrow at 3pm" for 1 hour

### 6. Meeting Search
- `GET /api/meetings/find/{description}` - Search meetings by description
  - Example: Find meetings with "Test" in the title

### 7. Contact Management
- `GET /api/contacts/search/{query}` - Search personal contacts
  - Searches name, email, company from personal_contacts.csv

### 8. Book with Contact
- `POST /api/meetings/book-with-contact` - Book meeting with contact by name
  - Example: Book with "Agostino" for "Friday at 1:30pm"

### 9. Meeting Management
- `GET /api/meetings/{id}` - Get meeting details
- `PATCH /api/meetings/{id}` - Update meeting
- `DELETE /api/meetings/{id}` - Cancel/delete meeting

### 10. Post-Meeting Automation
- `GET /api/meetings/{id}/notes` - Generate comprehensive meeting notes
  - Includes AI summary, transcript, action items
- `GET /api/meetings/{id}/download` - Get recording download URLs

### 11. Recording Management
- `GET /api/recordings` - List all recordings

## Test Results

The script outputs results with visual indicators:
- ✓ (green checkmark) - Test passed
- ✗ (red cross) - Test failed

For failures, detailed error messages are shown including:
- HTTP status code
- Error message
- Response text (first 200 chars)

## Test Summary

At the end, you get:
- Total tests run
- Number passed
- Number failed
- Pass rate percentage

## Requirements

```bash
pip install httpx
```

## Configuration

The script tests against:
```
http://zoom-mcp.theaiconsultant.co.uk:3001
```

To test against a different server, edit the `BASE_URL` variable in the script.

## Notes

- Some tests (like post-meeting automation) require actual completed meetings with recordings
- These will show as expected failures if no recordings are available
- Contact search requires `personal_contacts.csv` to be uploaded to the server
- Tests create temporary meetings that are automatically deleted

## Exit Codes

- `0` - All tests passed
- `1` - One or more tests failed or fatal error occurred
