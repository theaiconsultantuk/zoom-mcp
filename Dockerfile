# Zoom MCP Server - Docker Configuration
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY pyproject.toml ./
COPY LICENSE ./
COPY README.md ./
COPY src ./src

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Create directory for environment file
RUN mkdir -p /app/config

# Expose port (MCP typically uses stdio, but we'll expose for HTTP if needed)
EXPOSE 8080

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from zoom_mcp.server import create_zoom_mcp; create_zoom_mcp()" || exit 1

# Run the server
CMD ["python", "-m", "zoom_mcp.server"]
