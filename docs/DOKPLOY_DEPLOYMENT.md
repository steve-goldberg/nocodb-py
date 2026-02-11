# NocoDB MCP Server - Dokploy Deployment Guide

## Overview

Deploy the NocoDB MCP Server to Dokploy as an HTTP/SSE service that can be accessed by remote MCP clients.

## Prerequisites

- Dokploy instance running
- GitHub repo with the NocoDB MCP code
- NocoDB instance accessible from Dokploy server
- Domain configured in Dokploy (optional, can use port forwarding)

---

## Step 1: Create the Project in Dokploy

1. Go to **Projects** → **Create Project**
2. Name: `NocoDB MCP` or similar
3. Click **Create**

---

## Step 2: Add Application

1. Inside the project, click **+ Add Service** → **Application**
2. Choose **GitHub** as source
3. Connect your GitHub account if not already connected
4. Select repository: `your-username/nocodb` (or wherever the code lives)
5. Branch: `nocodb-mcp` (or `master` after merging)
6. Build Path: `/` (root of repo)

---

## Step 3: Configure Build Settings

Go to **General** tab:

| Setting | Value |
|---------|-------|
| Build Type | Dockerfile |
| Dockerfile Path | `Dockerfile` |
| Build Context | `.` |

---

## Step 4: Configure Environment Variables

Go to **Environment** tab and add these **Runtime Environment Variables**:

```
NOCODB_URL=https://nocodb.example.com
NOCODB_TOKEN=your-api-token-here
NOCODB_BASE_ID=your-base-id-here
NOCODB_VERIFY_SSL=false
```

**IMPORTANT:**
- Do NOT include `export` prefix
- Do NOT put quotes around values
- Each variable on its own line
- Toggle **"Create Environment File"** to **OFF** (Dokploy injects these at runtime)

### Why No Build-time Arguments?

The NocoDB MCP server reads environment variables at **runtime**, not build time. The Dockerfile doesn't need ARG directives because:
- The code is copied during build
- Environment variables are read when the container starts
- Secrets should never be baked into images anyway

---

## Step 5: Configure Domain (Optional)

Go to **Domains** tab:

If you want a public URL:
1. Click **Add Domain**
2. Enter: `mcp-nocodb.yourdomain.com` (or similar)
3. Enable HTTPS (Let's Encrypt)
4. Container Port: `8000`

If using internal only:
- Skip domain setup
- Access via `http://your-dokploy-ip:8000`

---

## Step 6: Configure Health Check

The server has a `/health` endpoint. Go to **Advanced** tab:

| Setting | Value |
|---------|-------|
| Health Check Path | `/health` |
| Health Check Interval | `30s` |
| Health Check Timeout | `10s` |

---

## Step 7: Deploy

1. Click **Deploy** button
2. Watch the build logs
3. Verify container starts successfully

### Expected Build Output

```
Step 1/8 : FROM python:3.12-slim
Step 2/8 : WORKDIR /app
Step 3/8 : RUN pip install uv
Step 4/8 : COPY . .
Step 5/8 : RUN uv pip install --system -e ".[mcp]"
Step 6/8 : ENV MCP_PORT=8000
Step 7/8 : ENV MCP_HOST=0.0.0.0
Step 8/8 : CMD ["python", "-m", "nocodb.mcp", "--http"]
```

### Expected Runtime Output

```
NocoDB MCP server connected to https://nocodb.example.com (base: your-base-id-here)
INFO     Starting MCP server 'NocoDB' with transport 'sse'
```

---

## Step 8: Verify Deployment

### Test Health Endpoint

```bash
curl https://mcp-nocodb.yourdomain.com/health
# or
curl http://your-dokploy-ip:8000/health
```

Expected response:
```json
{"status": "ok"}
```

### Test SSE Endpoint

The MCP SSE endpoint should be at:
```
https://mcp-nocodb.yourdomain.com/sse
```

---

## Troubleshooting

### "Missing required environment variables" Error

**Symptom:** Container crashes immediately with ValueError

**Fix:**
1. Go to Environment tab
2. Verify all 4 variables are set (no typos)
3. Click **Save**
4. **Redeploy** the application

### SSL Certificate Errors

**Symptom:** `SSLCertVerificationError: certificate verify failed`

**Fix:**
1. Ensure `NOCODB_VERIFY_SSL=false` is set
2. Redeploy

### Container Starts but Can't Connect

**Symptom:** Health check fails, can't reach endpoints

**Check:**
1. Is port 8000 exposed in Dokploy?
2. Is the domain/port mapping correct?
3. Check container logs for errors

### NocoDB Connection Refused

**Symptom:** `ConnectionError: Max retries exceeded`

**Check:**
1. Is NocoDB running and accessible from Dokploy server?
2. Can Dokploy server reach `nocodb.example.com`?
3. Is the token valid?

---

## Updating the Deployment

After pushing changes to GitHub:

1. Go to project in Dokploy
2. Click **Deploy** to rebuild
3. Or enable **Auto Deploy** in settings for automatic deploys on push

---

## Using with Remote MCP Clients

Once deployed, configure your MCP client to connect via SSE:

### Claude Desktop (Remote)

In `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "nocodb-remote": {
      "url": "https://mcp-nocodb.yourdomain.com/sse"
    }
  }
}
```

### Other MCP Clients

Use the SSE transport URL:
```
https://mcp-nocodb.yourdomain.com/sse
```

---

## Security Considerations

1. **API Token in Environment**: The token is stored in Dokploy's encrypted environment storage
2. **SSL Bypass**: Only use `NOCODB_VERIFY_SSL=false` for self-signed certs on trusted networks
3. **Network Access**: Consider restricting access to the MCP endpoint (firewall, VPN, etc.)
4. **Token Rotation**: If you regenerate the NocoDB token, update Dokploy env vars and redeploy

---

## Architecture Diagram

```
┌─────────────────┐     HTTPS/SSE      ┌──────────────────┐
│  Claude Desktop │ ◄───────────────► │  Dokploy Server  │
│  (MCP Client)   │                    │  (MCP Server)    │
└─────────────────┘                    └────────┬─────────┘
                                                │
                                                │ HTTPS (verify=false)
                                                ▼
                                       ┌──────────────────┐
                                       │  NocoDB Instance │
                                       │  (Pangolin)      │
                                       └──────────────────┘
```

---

## Files Reference

| File | Purpose |
|------|---------|
| `Dockerfile` | Build image with Python 3.12 + uv + FastMCP |
| `docker-compose.yml` | Local testing (not used by Dokploy) |
| `.env` | Local development only |
| `nocodb/mcp/__main__.py` | Entry point, handles --http flag |
| `nocodb/mcp/dependencies.py` | Reads env vars at runtime |
