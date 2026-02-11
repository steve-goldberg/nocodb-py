FROM python:3.12-slim

WORKDIR /app

# Install the package with MCP dependencies
COPY . .
RUN pip install --no-cache-dir -e ".[mcp]"

# Default port
ENV MCP_PORT=8000
ENV MCP_HOST=0.0.0.0

EXPOSE 8000

# Run HTTP server
CMD ["python", "-m", "nocodb.mcp", "--http"]
