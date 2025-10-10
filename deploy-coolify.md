# Deploying Zoom MCP Server with Coolify

Complete guide for deploying your Zoom MCP server using Coolify on Hostinger.

---

## What is Coolify?

Coolify is a self-hosted platform (like Heroku/Vercel) that makes deploying Docker applications incredibly easy. It handles:
- ✅ Docker builds and deployments
- ✅ Environment variables
- ✅ SSL certificates (automatic)
- ✅ Reverse proxy
- ✅ Zero-downtime deployments
- ✅ Automatic rebuilds on git push

---

## Prerequisites

✅ **You have:**
- Coolify installed on Hostinger server
- GitHub account
- Zoom API credentials

✅ **You need:**
- 10 minutes
- GitHub repository (we'll create this)

---

## Step 1: Push to GitHub

### 1.1 Initialize Git Repository

```bash
cd /Volumes/Courses/Scripts/Python/MCP/zoom-mcp

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Zoom MCP server with enhanced tools"
```

### 1.2 Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `zoom-mcp`
3. Description: `Zoom MCP Server with enhanced API tools`
4. **Keep it Private** (recommended - contains API integration code)
5. **Don't initialize** with README (we already have code)
6. Click "Create repository"

### 1.3 Push to GitHub

```bash
# Add remote (replace YOUR-USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR-USERNAME/zoom-mcp.git

# Push to main branch
git branch -M main
git push -u origin main
```

**✅ Verify:** Visit your GitHub repo - all files should be there except `.env`

---

## Step 2: Configure Coolify

### 2.1 Access Coolify Dashboard

1. Open your Coolify dashboard (e.g., https://coolify.yourdomain.com)
2. Log in with your credentials

### 2.2 Create New Application

1. Click **"+ New Resource"**
2. Select **"Application"**
3. Choose **"Public Repository"** (or connect GitHub if you want private repo)

### 2.3 Configure Repository

**Repository URL:**
```
https://github.com/YOUR-USERNAME/zoom-mcp
```

**Branch:** `main`

**Build Pack:** Docker

**Port:** `8080` (or leave default)

### 2.4 Set Environment Variables

Click on **"Environment Variables"** and add:

```bash
ZOOM_API_KEY=your-client-id-here
ZOOM_API_SECRET=your-client-secret-here
ZOOM_ACCOUNT_ID=your-account-id-here
```

**Important:** Mark these as **"Build Time"** and **"Runtime"** variables

### 2.5 Configure Build Settings

**Dockerfile Path:** `./Dockerfile` (should auto-detect)

**Port Mapping:**
- **Container Port:** 8080
- **Public Port:** 80 (or 443 for HTTPS)

### 2.6 Domain Configuration

**Option A: Use Coolify Subdomain**
- Coolify will assign: `zoom-mcp-xxxx.coolify.yourdomain.com`

**Option B: Use Custom Domain**
1. Add your domain: `zoom-mcp.yourdomain.com`
2. Coolify will automatically handle SSL with Let's Encrypt

---

## Step 3: Deploy

### 3.1 Start Deployment

1. Click **"Deploy"** button
2. Coolify will:
   - Pull from GitHub ✅
   - Build Docker image ✅
   - Start container ✅
   - Configure reverse proxy ✅
   - Generate SSL certificate ✅

### 3.2 Monitor Deployment

Watch the build logs in real-time. You should see:

```
[INFO] Cloning repository...
[INFO] Building Docker image...
[INFO] Installing dependencies...
[INFO] Starting container...
[SUCCESS] Deployment successful!
```

**Expected time:** 2-5 minutes

---

## Step 4: Verify Deployment

### 4.1 Check Application Status

In Coolify dashboard:
- Status should show **"Running" (green)**
- URL should be clickable

### 4.2 Test Health Endpoint

```bash
# Replace with your Coolify URL
curl https://zoom-mcp-xxxx.coolify.yourdomain.com/health
```

**Expected response:** `OK` or `200 OK`

### 4.3 Test MCP Tools

```bash
# Test in Coolify logs or via curl
curl -X POST https://your-coolify-url/mcp \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/list"}'
```

**Expected:** JSON response with list of 8 tools

---

## Step 5: Configure for Gumloop

### 5.1 Get Your Server URL

From Coolify dashboard, copy your application URL:
```
https://zoom-mcp-xxxx.coolify.yourdomain.com
```

### 5.2 Configure Gumloop

In Gumloop's "Ask AI" node with remote MCP server:

1. **Server Type:** Remote MCP Server
2. **Server URL:** `https://zoom-mcp-xxxx.coolify.yourdomain.com`
3. **Authentication:** (if you add it later)

---

## Step 6: Enable Auto-Deploy (Optional)

### 6.1 Configure Webhook

1. In Coolify → Your App → **"Deployments"**
2. Enable **"Automatic Deployment"**
3. Copy the webhook URL

### 6.2 Add to GitHub

1. Go to GitHub repo → Settings → Webhooks
2. Add webhook URL from Coolify
3. Trigger: `push` events
4. Content type: `application/json`

**Now:** Every `git push` will auto-deploy! 🚀

---

## Coolify-Specific Configuration

### Update Dockerfile for Coolify (Optional Enhancement)

If you want health checks and better Coolify integration:

**Add to Dockerfile:**
```dockerfile
# Health check endpoint
EXPOSE 8080
ENV PORT=8080

# Add health check for Coolify
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8080/health || exit 1
```

### Resource Limits (Optional)

In Coolify → Resource Limits:
- **CPU:** 0.5 cores (adjust based on load)
- **Memory:** 512MB (should be plenty)
- **Storage:** 1GB

---

## Updating Your Application

### Method 1: Git Push (Recommended)

```bash
# Make your changes locally
cd /Volumes/Courses/Scripts/Python/MCP/zoom-mcp

# Commit changes
git add .
git commit -m "Update: added new feature"

# Push to GitHub
git push origin main

# Coolify will auto-deploy (if webhook configured)
# Or click "Deploy" in Coolify dashboard
```

### Method 2: Coolify Dashboard

1. Click **"Redeploy"** button
2. Coolify will pull latest from GitHub
3. Rebuild and restart

---

## Environment Variables Management

### Adding New Variables

1. Coolify Dashboard → Your App → **"Environment Variables"**
2. Click **"+ Add Variable"**
3. Add key and value
4. Mark as **Build** and/or **Runtime**
5. Click **"Redeploy"** to apply

### Updating Variables

1. Edit variable in Coolify UI
2. Click **"Redeploy"**
3. New values will be used

**Note:** Variables are encrypted in Coolify database

---

## Monitoring and Logs

### View Logs

1. Coolify Dashboard → Your App → **"Logs"**
2. Real-time log streaming
3. Filter by:
   - Build logs
   - Runtime logs
   - Error logs

### Common Log Locations

**Build Logs:**
```
[INFO] Installing dependencies...
[INFO] Building image...
```

**Runtime Logs:**
```
2025-10-10 02:42:57,385 - mcp.server.lowlevel.server - INFO - Processing request
2025-10-10 02:42:57,407 - zoom_mcp.resources.recordings - INFO - RecordingResource initialized
```

**Error Logs:**
```
[ERROR] Failed to connect to Zoom API
```

---

## Troubleshooting

### Issue: Build Fails

**Check:**
1. Dockerfile syntax
2. pyproject.toml dependencies
3. Build logs in Coolify

**Fix:**
```bash
# Test build locally first
docker build -t zoom-mcp-test .

# If it works locally, push to GitHub
git push origin main
```

### Issue: Container Crashes

**Check:**
1. Runtime logs
2. Environment variables set correctly
3. Port configuration

**Debug:**
```bash
# In Coolify, check container logs
# Look for Python errors or missing env vars
```

### Issue: Can't Connect to Server

**Check:**
1. Application status (should be "Running")
2. Port mapping (8080 → 80/443)
3. Firewall rules (Coolify handles this usually)

**Test:**
```bash
# Test from Coolify server
curl http://localhost:8080/health

# Test from outside
curl https://your-coolify-url/health
```

### Issue: Environment Variables Not Loading

**Fix:**
1. Verify variables are set in Coolify UI
2. Check both "Build Time" and "Runtime" are selected
3. Redeploy application

---

## Security Best Practices

### 1. Keep Secrets in Coolify
✅ **Do:** Store all secrets in Coolify environment variables
❌ **Don't:** Commit secrets to GitHub

### 2. Use Private Repository
✅ **Recommended:** Keep GitHub repo private
⚠️ **If public:** Double-check no secrets in code

### 3. Enable HTTPS
✅ Coolify handles this automatically with Let's Encrypt

### 4. Regular Updates
```bash
# Update dependencies periodically
cd /Volumes/Courses/Scripts/Python/MCP/zoom-mcp
git pull origin main
# Review and update pyproject.toml if needed
git push origin main
```

---

## Scaling and Performance

### Horizontal Scaling

Coolify supports running multiple instances:

1. Dashboard → Your App → **"Scale"**
2. Increase replicas (e.g., 2 or 3)
3. Coolify handles load balancing automatically

### Vertical Scaling

Increase resources:

1. Dashboard → Your App → **"Resources"**
2. Adjust CPU/Memory limits
3. Redeploy

### Performance Tips

1. **Enable caching** for OAuth tokens (in code)
2. **Use connection pooling** for HTTP requests
3. **Monitor logs** for slow requests
4. **Set up alerts** in Coolify

---

## Backup and Recovery

### Backup Configuration

Coolify automatically backs up:
- ✅ Environment variables
- ✅ Application configuration
- ✅ Deployment history

### Manual Backup

```bash
# Backup environment variables
# Export from Coolify UI → Download .env file

# Backup code (it's in GitHub)
git clone https://github.com/YOUR-USERNAME/zoom-mcp.git

# Backup Coolify database (on server)
# Coolify handles this automatically
```

### Disaster Recovery

If something goes wrong:

1. **Rollback Deployment:**
   - Coolify → Deployments → Select previous version → Redeploy

2. **Restore from GitHub:**
   - `git reset --hard <previous-commit>`
   - `git push origin main`

3. **Fresh Deploy:**
   - Delete application in Coolify
   - Create new application
   - Reconfigure environment variables
   - Deploy

---

## Cost Optimization

### Resource Usage

Monitor in Coolify:
- CPU usage (should be low, ~5-10%)
- Memory usage (~200-300MB)
- Network (minimal)

### Optimization Tips

1. **Use caching** for API tokens
2. **Limit log retention** (7 days is usually enough)
3. **Scale down** when not in use (if applicable)
4. **Monitor** for resource leaks

---

## Advanced Configuration

### Custom Docker Build Args

In Coolify → Build Args:
```
PYTHON_VERSION=3.11
```

### Custom Startup Command

Override CMD in Dockerfile:
```dockerfile
CMD ["python", "-m", "zoom_mcp.server", "--port", "8080"]
```

### Health Check Configuration

Customize in Dockerfile:
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1
```

---

## Comparison: Coolify vs Manual VPS

| Feature | Coolify ⭐ | Manual VPS |
|---------|----------|------------|
| **Setup Time** | 10 mins | 30 mins |
| **SSL Setup** | Automatic | Manual |
| **Updates** | Git push | SSH + Docker commands |
| **Monitoring** | Built-in UI | Manual setup |
| **Rollbacks** | One click | Manual |
| **Scaling** | UI button | Manual config |
| **Zero Downtime** | Yes | Manual setup |
| **Best For** | You! ✅ | Advanced users |

---

## Quick Reference

### Common Commands

**Local Development:**
```bash
# Make changes
git add .
git commit -m "Update"
git push origin main
```

**Coolify Dashboard:**
- Deploy: Click "Deploy" button
- Logs: Click "Logs" tab
- Env Vars: Click "Environment Variables"
- Scale: Click "Scale" section

**Testing:**
```bash
# Health check
curl https://your-url/health

# Test tool
curl -X POST https://your-url/mcp \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/list"}'
```

---

## Support and Resources

- **Coolify Docs:** https://coolify.io/docs
- **Coolify Discord:** https://discord.gg/coolify
- **Your Server:** https://coolify.yourdomain.com

---

## Next Steps After Deployment

1. ✅ Test all 8 MCP tools
2. ✅ Configure Gumloop connection
3. ✅ Set up monitoring/alerts
4. ✅ Enable auto-deploy webhook
5. ✅ Document your Gumloop workflows

---

**Ready to deploy?** Follow Steps 1-4 above and you'll be running in 10 minutes! 🚀

**Last Updated:** October 10, 2025
