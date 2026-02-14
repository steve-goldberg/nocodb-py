FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# Install Python dependencies first (cached layer)
COPY pyproject.toml LICENSE ./
RUN mkdir -p nocobot && touch nocobot/__init__.py && \
    uv pip install --system --no-cache . && \
    rm -rf nocobot

# Copy the full source and install
COPY . .
RUN uv pip install --system --no-cache .

# Create config directory
RUN mkdir -p /root/.nocobot

ENTRYPOINT ["nocobot"]
