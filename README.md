# Zoom MCP Server

A Model Context Protocol (MCP) server implementation for Zoom, providing AI models with access to Zoom's API capabilities.

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/zoom-mcp.git
cd zoom-mcp
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e .
```

4. Set up environment variables:
```bash
cp .env.example .env
```
Edit `.env` with your Zoom API credentials:
- `ZOOM_API_KEY`: Your Zoom API Key (Client ID)
- `ZOOM_API_SECRET`: Your Zoom API Secret (Client Secret)
- `ZOOM_ACCOUNT_ID`: Your Zoom Account ID (optional)

## Development

### Running Tests
```bash
pytest
```

### Code Style
This project follows PEP 8 guidelines. You can check your code style using:
```bash
flake8 src tests
```

## Authentication

This project uses Zoom's Server-to-Server OAuth 2.0 authentication. The authentication module handles:
- JWT token generation
- Token caching and renewal
- Environment variable configuration

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 