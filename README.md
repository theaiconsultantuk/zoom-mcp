# Zoom MCP Server

A Model Context Protocol (MCP) server implementation for Zoom, providing AI models with access to Zoom's API capabilities through both MCP tools and REST API endpoints.

## Overview

This project implements a comprehensive MCP server that enables Claude and other AI models to connect to Zoom, retrieve data, and perform actions through the Zoom API. It serves as a bridge between AI assistants and Zoom, allowing for seamless integration and intelligent automation of Zoom meetings, contacts, and recordings.

**Version 2.0.0** includes advanced features like natural language date parsing, contact-based meeting booking, and AI-powered post-meeting automation.

## ✨ Key Features

### 🤖 Natural Language Meeting Booking
- Book meetings using natural language: "tomorrow at 3pm", "next Friday morning"
- Smart duration parsing: "1 hour", "45 minutes", "90 min"
- Timezone-aware scheduling with automatic conversion
- Integration with personal contacts for easy booking

### 👥 Contact Management
- Search personal contacts by name, email, or company
- Book meetings directly with contacts by name
- CSV-based contact storage for privacy and control

### 📝 Post-Meeting Automation
- AI-generated meeting notes and summaries
- Automatic transcript extraction
- Action item detection
- Recording download links

### 📅 Meeting Management
- Create, update, and cancel meetings
- Search meetings by description
- List today's and upcoming meetings
- Meeting templates for recurring formats

### 🔐 Enterprise-Ready
- Server-to-Server OAuth 2.0 authentication
- RESTful API with comprehensive endpoints
- MCP protocol support for AI integration
- Debug mode for troubleshooting

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- A Zoom account with admin privileges
- A Zoom Server-to-Server OAuth app with appropriate scopes
- [uv](https://github.com/astral-sh/uv) for Python package management
- Node.js 18+ (for Claude Desktop integration)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/theaiconsultantuk/zoom-mcp.git
   cd zoom-mcp
   ```

2. **Create virtual environment and install dependencies:**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e .
   ```

3. **Set up Zoom API credentials:**
   ```bash
   python scripts/setup_zoom_auth.py
   ```

   This creates a `.env` file with:
   ```env
   ZOOM_API_KEY=your-client-id
   ZOOM_API_SECRET=your-client-secret
   ZOOM_ACCOUNT_ID=your-account-id
   ```

4. **Configure personal contacts (optional):**
   ```bash
   # Create personal_contacts.csv with your contacts
   echo "name,email,phone,company" > personal_contacts.csv
   echo "John Doe,john@example.com,+1234567890,Acme Corp" >> personal_contacts.csv
   ```

5. **Start the servers:**
   ```bash
   # Start MCP server (SSE on port 3000, REST on port 3001)
   python -m zoom_mcp.server
   ```

### Required Zoom Scopes

Enable these scopes in your Zoom Server-to-Server OAuth app:

**Essential:**
- `user:read:admin` - User information
- `meeting:write:admin` - Create/update meetings
- `meeting:read:admin` - Read meeting details
- `recording:read:admin` - Access recordings

**Optional (for full functionality):**
- `meeting:read:meeting_summary:admin` - AI meeting summaries
- `contact:read:list_contacts` - Contact management

## 📖 Usage

### Testing the Installation

Run the comprehensive test suite:

```bash
./scripts/test_all_endpoints.py
# or
python3 scripts/test_all_endpoints.py
```

This verifies:
- ✓ OAuth token generation
- ✓ API connectivity
- ✓ All endpoint functionality
- ✓ Natural language parsing
- ✓ Contact search
- ✓ Meeting operations

### REST API Endpoints

The server exposes a comprehensive REST API on **port 3001**:

#### 👤 User Management
```bash
GET /api/users              # List all users
GET /api/users/me           # Current user details
GET /api/users/{user_id}    # Specific user
```

#### 📅 Meetings
```bash
# List meetings
GET /api/meetings/today              # Today's meetings
GET /api/meetings/templates          # Meeting templates

# Create meetings
POST /api/meetings/create?topic=Meeting&start_time=2025-10-17T10:00:00Z&duration=60

# Natural language booking
POST /api/meetings/book-natural?description=tomorrow at 3pm&topic=Strategy Review&duration=1 hour

# Search and manage
GET /api/meetings/find/{description}  # Search by keyword
GET /api/meetings/{meeting_id}        # Get meeting details
PATCH /api/meetings/{meeting_id}      # Update meeting
DELETE /api/meetings/{meeting_id}     # Cancel meeting
```

#### 👥 Contacts
```bash
GET /api/contacts                    # List contacts
GET /api/contacts/search/{query}     # Search by name/email/company

# Book with contact
POST /api/meetings/book-with-contact?description=Friday at 2pm&contact_name=John&topic=Review
```

#### 📹 Recordings & Post-Meeting
```bash
GET /api/recordings                        # List all recordings
GET /api/meetings/{id}/notes              # AI-generated meeting notes
GET /api/meetings/{id}/download           # Recording download links
```

### MCP Tools (for Claude Desktop)

The MCP server provides these tools for AI assistants:

- `list_users` - Get Zoom account users
- `get_user` - Retrieve specific user details
- `list_meetings` - Access meeting information
- `get_meeting` - Detailed meeting data
- `list_recordings` - Available recordings
- `search_personal_contacts` - Find contacts
- `get_contact_by_name` - Contact lookup

### Examples

#### Natural Language Meeting Booking

```bash
# Book a meeting for tomorrow afternoon
curl -X POST "http://localhost:3001/api/meetings/book-natural?description=tomorrow%20at%203pm&topic=Team%20Sync&duration=45%20minutes"

# Book with a contact
curl -X POST "http://localhost:3001/api/meetings/book-with-contact?description=next%20Friday%20morning&contact_name=Sarah&topic=Project%20Review"
```

#### Search Contacts

```bash
# Find contacts by name
curl "http://localhost:3001/api/contacts/search/John"

# Search by company
curl "http://localhost:3001/api/contacts/search/Acme"
```

#### Get Meeting Notes

```bash
# Get AI-generated notes for a completed meeting
curl "http://localhost:3001/api/meetings/87420530060/notes"
```

## Authentication

This project uses Zoom's Server-to-Server OAuth 2.0 authentication. The authentication module handles:
- OAuth 2.0 token generation
- Token caching and renewal
- Environment variable configuration

The authentication flow:
1. Base64 encode the API Key and Secret for Basic authentication
2. Request an access token from Zoom's OAuth endpoint
3. Use the token for subsequent API requests
4. Automatically refresh the token when it expires

## 🔧 Claude Desktop Integration

To use with Claude Desktop, add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "zoom": {
      "command": "node",
      "args": [
        "/path/to/zoom-mcp/scripts/mcp-sse-client.js",
        "http://your-server:3000/sse"
      ],
      "env": {
        "NODE_PATH": "/path/to/zoom-mcp/scripts/node_modules"
      }
    }
  }
}
```

Then install the SSE client dependencies:
```bash
cd scripts
npm install @modelcontextprotocol/sdk
```

## 🧪 Development

### Creating a Zoom App

1. Go to the [Zoom App Marketplace](https://marketplace.zoom.us/)
2. Click "Develop" → "Build App"
3. Choose "Server-to-Server OAuth"
4. Configure scopes (see Required Zoom Scopes above)
5. Get your credentials: Account ID, Client ID, Client Secret

### Running Tests

```bash
# Comprehensive API tests
python3 scripts/test_all_endpoints.py

# Unit tests
python -m pytest

# Code style check
uv pip install flake8
flake8 src tests
```

### Project Structure

```
zoom-mcp/
├── src/zoom_mcp/
│   ├── server.py              # MCP server implementation
│   ├── api.py                 # REST API endpoints
│   ├── auth/                  # OAuth authentication
│   ├── tools/                 # MCP tools & features
│   │   ├── date_parser.py    # Natural language date parsing
│   │   ├── personal_contacts.py  # Contact management
│   │   ├── meeting_management.py # Meeting CRUD operations
│   │   └── meeting_notes.py  # Post-meeting automation
├── scripts/
│   ├── test_all_endpoints.py # Comprehensive test suite
│   ├── mcp-sse-client.js     # Claude Desktop bridge
│   └── setup_zoom_auth.py    # Auth setup wizard
├── personal_contacts.csv      # Your contacts (gitignored)
└── .env                       # API credentials (gitignored)
```

### Adding New Features

1. Create tool in `src/zoom_mcp/tools/`
2. Register in `server.py` for MCP
3. Add endpoint in `api.py` for REST API
4. Update tests in `scripts/test_all_endpoints.py`
5. Document in README.md

## 🧩 Features in Detail

### Natural Language Date Parsing

Supports various formats:
- **Relative:** "tomorrow", "next Friday", "in 2 hours"
- **Time of day:** "morning" (9am), "afternoon" (2pm), "evening" (6pm)
- **Specific times:** "at 3pm", "at 10:30am"
- **Combinations:** "tomorrow afternoon", "next Monday at 2pm"

Timezone support:
- Default: Europe/London
- Configurable per request
- Automatic conversion to Zoom's required format

### Contact-Based Booking

1. Add contacts to `personal_contacts.csv`:
   ```csv
   name,email,phone,company
   Sarah Johnson,sarah@example.com,+1234567890,Acme Corp
   John Smith,john@techco.com,+9876543210,TechCo
   ```

2. Book meeting by name:
   ```bash
   POST /api/meetings/book-with-contact?contact_name=Sarah&description=tomorrow at 3pm
   ```

### Post-Meeting Automation

After meetings complete with recordings:
```bash
# Get comprehensive notes
GET /api/meetings/{id}/notes

Response:
{
  "meeting_details": {...},
  "ai_summary": "Discussion about Q4 goals...",
  "transcript": "Full meeting transcript...",
  "action_items": ["Follow up with team", "Send report"],
  "recording_details": {...}
}
```

## 🐛 Troubleshooting

### Authentication Issues

**Problem:** "Invalid access token" errors

**Solutions:**
1. Verify credentials in `.env`:
   ```bash
   cat .env | grep ZOOM_
   ```
2. Deactivate and reactivate app in Zoom Marketplace
3. Check Account ID matches your Zoom account
4. Ensure all required scopes are enabled

### Permission Errors

**Problem:** 400/403 errors for specific endpoints

**Solutions:**
1. Check scope requirements in Zoom App settings
2. Compare enabled scopes with Required Scopes section
3. Some features require specific Zoom plan levels

### Natural Language Parsing Issues

**Problem:** Date parsing returns unexpected times

**Solutions:**
1. Always specify timezone explicitly
2. Use ISO format for precision: `2025-10-17T15:00:00Z`
3. Check server's default timezone setting

### Contact Search Returns Empty

**Problem:** Contact searches return no results

**Solutions:**
1. Verify `personal_contacts.csv` exists in project root
2. Check CSV format (name,email,phone,company)
3. Ensure file is uploaded to server (if deployed remotely)
4. CSV file should not have BOM or special encoding

### Testing Failures

**Problem:** Test suite shows failures

**Solutions:**
1. Check server is running: `curl http://localhost:3001/`
2. Verify version 2.0.0 is deployed
3. Review failed test error messages
4. Check Zoom API rate limits

## 📊 Test Results

**Latest Test Run:** 92% Pass Rate (12/13 tests)

✅ **All Core Features Working:**
- User management
- Meeting creation and management
- Contact search
- Recording access
- Post-meeting automation
- Natural language booking (with query params)

See `scripts/README_TESTING.md` for full test documentation.

## 🚢 Deployment

### VPS Deployment (Coolify/Docker)

1. Push to GitHub
2. Configure Coolify to watch your repo
3. Set environment variables in Coolify:
   - `ZOOM_API_KEY`
   - `ZOOM_API_SECRET`
   - `ZOOM_ACCOUNT_ID`
4. Expose ports:
   - 3000 (SSE/MCP)
   - 3001 (REST API)

### Local Development

```bash
# Run in development mode with auto-reload
uvicorn zoom_mcp.api:app --reload --port 3001
```

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Follow existing code style (PEP 8)
4. Add tests for new features
5. Update documentation
6. Commit changes (`git commit -m 'Add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open Pull Request

### Development Guidelines

- Write tests for all new features
- Update API documentation
- Follow semantic versioning
- Include examples in docstrings
- Run test suite before committing

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp)
- Integrates with [Zoom API](https://developers.zoom.us/)
- Supports [Model Context Protocol](https://modelcontextprotocol.io/)

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/theaiconsultantuk/zoom-mcp/issues)
- **Documentation:** See `scripts/README_TESTING.md`
- **API Reference:** Visit `http://your-server:3001/` for live API docs

---

**Version 2.0.0** | Built with ❤️ for AI-powered Zoom automation 