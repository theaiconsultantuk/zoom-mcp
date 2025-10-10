# Deploy to Coolify - Quick Start Guide

Your personalized deployment guide for Coolify.

---

## ✅ Prerequisites Complete

Your code is already on GitHub at:
**https://github.com/theaiconsultantuk/zoom-mcp**

Everything is ready to deploy:
- ✅ All 8 tools implemented
- ✅ Docker configuration
- ✅ OAuth fixes
- ✅ Documentation
- ✅ .env excluded from repo

---

## Step 1: Configure Coolify

### 1.1 Access Coolify
Open your Coolify dashboard on Hostinger

### 1.2 Create New Application

1. Click **"+ New Resource"**
2. Select **"Application"**
3. Choose **"Public Repository"** or connect GitHub OAuth

### 1.3 Repository Settings

**Repository URL:**
```
https://github.com/theaiconsultantuk/zoom-mcp
```

**Branch:** `main`

**Build Pack:** Docker (will auto-detect from Dockerfile)

### 1.4 Environment Variables

Click **"Environment Variables"** and add these three:

```bash
ZOOM_API_KEY=your-client-id-here
```

```bash
ZOOM_API_SECRET=your-client-secret-here
```

```bash
ZOOM_ACCOUNT_ID=your-account-id-here
```

**Important:**
- Mark each as **"Build Time"** ✅
- Mark each as **"Runtime"** ✅
- These are encrypted by Coolify and never exposed

### 1.5 Port Configuration

**Container Port:** 8080
**Public Port:** 80 (or 443 for HTTPS)

Coolify will handle the mapping automatically.

### 1.6 Domain (Optional but Recommended)

**Option A: Coolify Subdomain**
- Auto-assigned: `zoom-mcp-xxxx.yourserver.com`

**Option B: Custom Domain**
- Add: `zoom-mcp.yourdomain.com`
- Coolify handles SSL automatically

---

## Step 2: Deploy!

1. Click **"Deploy"** button
2. Watch the build logs
3. Wait 2-5 minutes

**Expected output:**
```
✓ Cloning repository
✓ Building Docker image
✓ Installing Python dependencies
✓ Starting container
✓ Configuring reverse proxy
✓ Generating SSL certificate
✓ Deployment successful!
```

---

## Step 3: Test Your Deployment

### Test 1: Health Check

```bash
# Replace with your Coolify URL
curl https://zoom-mcp-xxxx.yourserver.com/health
```

**Expected:** `OK` or `200 OK`

### Test 2: List Tools

```bash
curl -X POST https://zoom-mcp-xxxx.yourserver.com/mcp \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/list"}'
```

**Expected:** JSON with 8 tools

---

## Step 4: Configure for Gumloop

In Gumloop's MCP integration:

**Server URL:**
```
https://zoom-mcp-xxxx.yourserver.com
```

Replace `zoom-mcp-xxxx.yourserver.com` with your actual Coolify URL.

---

## Future Updates

### To Update Your Server:

```bash
# Make changes locally
cd /Volumes/Courses/Scripts/Python/MCP/zoom-mcp

# Commit and push
git add .
git commit -m "Updated feature X"
git push origin main

# Then in Coolify:
# - Click "Redeploy" button
# - Or set up auto-deploy webhook (see below)
```

### Enable Auto-Deploy (Optional):

1. Coolify → Your App → **"Deployments"**
2. Enable **"Automatic Deployment"**
3. Copy webhook URL
4. GitHub → Settings → Webhooks → Add webhook
5. Now every `git push` auto-deploys! 🚀

---

## Troubleshooting

### Build Fails?
1. Check Coolify build logs
2. Verify Dockerfile syntax
3. Test locally: `docker build -t test .`

### Container Crashes?
1. Check Coolify runtime logs
2. Verify environment variables are set
3. Test locally: `docker-compose up`

### Can't Connect?
1. Check application status (should be "Running")
2. Verify port mapping
3. Test from Coolify server: `curl localhost:8080/health`

---

## Quick Reference

### Your GitHub Repo
https://github.com/theaiconsultantuk/zoom-mcp

### Required Environment Variables
- ZOOM_API_KEY
- ZOOM_API_SECRET
- ZOOM_ACCOUNT_ID

### Container Port
8080

### Health Check Endpoint
/health

---

## What's Deployed

Your enhanced Zoom MCP server with:

✅ **8 Tools:**
1. list_todays_meetings - Get today's meetings
2. list_meetings - List meetings with filters
3. get_meeting - Get meeting details
4. list_recordings - List cloud recordings
5. get_recording_transcript - Get recording transcripts
6. list_users - List account users
7. get_user - Get user details

✅ **Features:**
- Server-to-Server OAuth authentication
- Docker containerized
- Auto-scaling ready
- SSL/HTTPS enabled
- Health monitoring
- Comprehensive logging

---

## Next Steps After Deployment

1. ✅ Test all 8 tools in Gumloop
2. ✅ Set up webhook for auto-deploy
3. ✅ Monitor logs in Coolify
4. ✅ Build your Gumloop workflows
5. ✅ Enjoy! 🎉

---

**Estimated Time:** 10 minutes total
**Difficulty:** Easy ⭐⭐☆☆☆

---

**Need help?** Check the detailed guide in `deploy-coolify.md`

**Last Updated:** October 10, 2025
