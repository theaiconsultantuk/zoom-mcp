# Deploying Zoom MCP Server to VPS

Complete guide for deploying the Zoom MCP server to your VPS using Docker.

---

## Prerequisites

### On Your VPS
- ✅ Docker installed
- ✅ Docker Compose installed
- ✅ Port 8080 available (or choose another port)
- ✅ Domain name pointed to your VPS (optional but recommended)
- ✅ SSL certificate (optional but recommended for production)

### On Your Local Machine
- ✅ SSH access to your VPS
- ✅ Git installed (or scp/rsync for file transfer)

---

## Step 1: Prepare Your VPS

### SSH into Your VPS
```bash
ssh your-username@your-vps-ip
```

### Install Docker (if not already installed)
```bash
# Update packages
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

### Create Application Directory
```bash
mkdir -p ~/apps/zoom-mcp
cd ~/apps/zoom-mcp
```

---

## Step 2: Transfer Files to VPS

### Option A: Using Git (Recommended)

**On your local machine:**
```bash
cd /Volumes/Courses/Scripts/Python/MCP/zoom-mcp

# Initialize git repo if not already done
git init
git add .
git commit -m "Initial commit - Zoom MCP server"

# Push to your Git hosting (GitHub, GitLab, etc.)
git remote add origin https://github.com/yourusername/zoom-mcp.git
git push -u origin main
```

**On your VPS:**
```bash
cd ~/apps/zoom-mcp
git clone https://github.com/yourusername/zoom-mcp.git .
```

### Option B: Using SCP

**On your local machine:**
```bash
cd /Volumes/Courses/Scripts/Python/MCP/zoom-mcp

# Create a tarball excluding unnecessary files
tar -czf zoom-mcp.tar.gz \
  --exclude='.venv' \
  --exclude='__pycache__' \
  --exclude='.git' \
  --exclude='tests' \
  src/ pyproject.toml Dockerfile docker-compose.yml .env.example

# Transfer to VPS
scp zoom-mcp.tar.gz your-username@your-vps-ip:~/apps/zoom-mcp/

# SSH to VPS and extract
ssh your-username@your-vps-ip
cd ~/apps/zoom-mcp
tar -xzf zoom-mcp.tar.gz
rm zoom-mcp.tar.gz
```

### Option C: Using rsync (Recommended for updates)

**On your local machine:**
```bash
rsync -avz --exclude='.venv' --exclude='__pycache__' --exclude='.git' \
  /Volumes/Courses/Scripts/Python/MCP/zoom-mcp/ \
  your-username@your-vps-ip:~/apps/zoom-mcp/
```

---

## Step 3: Configure Environment Variables

**On your VPS:**
```bash
cd ~/apps/zoom-mcp

# Copy example env file
cp .env.example .env

# Edit with your credentials
nano .env
```

**Add your Zoom credentials:**
```env
ZOOM_API_KEY=WRv5JXlFSXSZ5jmGtvznw
ZOOM_API_SECRET=4qqxMKsGjLZ8ooQN42NLbHce5OdoTE2V
ZOOM_ACCOUNT_ID=mk8MCWYUT2-Er1nzO4LkAg
```

**Save and exit:** Ctrl+X, then Y, then Enter

---

## Step 4: Build and Run with Docker

### Build the Docker Image
```bash
cd ~/apps/zoom-mcp
docker-compose build
```

### Start the Server
```bash
docker-compose up -d
```

### Verify It's Running
```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs -f zoom-mcp

# Check health
docker-compose exec zoom-mcp python -c "from zoom_mcp.server import create_zoom_mcp; print('Server OK')"
```

---

## Step 5: Set Up Reverse Proxy (Nginx)

For production use with HTTPS, set up Nginx as a reverse proxy.

### Install Nginx
```bash
sudo apt install nginx -y
```

### Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/zoom-mcp
```

**Add this configuration:**
```nginx
server {
    listen 80;
    server_name zoom-mcp.yourdomain.com;  # Replace with your domain

    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Increase timeouts for long-running MCP connections
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
    }
}
```

**Enable the site:**
```bash
sudo ln -s /etc/nginx/sites-available/zoom-mcp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Step 6: Set Up SSL with Let's Encrypt (Optional but Recommended)

### Install Certbot
```bash
sudo apt install certbot python3-certbot-nginx -y
```

### Get SSL Certificate
```bash
sudo certbot --nginx -d zoom-mcp.yourdomain.com
```

Follow the prompts and choose to redirect HTTP to HTTPS.

---

## Step 7: Configure Firewall

```bash
# Allow SSH
sudo ufw allow OpenSSH

# Allow HTTP and HTTPS
sudo ufw allow 'Nginx Full'

# Enable firewall
sudo ufw enable
```

---

## Step 8: Set Up Auto-Restart on Boot

Docker Compose already has `restart: unless-stopped`, but let's ensure it starts on boot:

```bash
# Enable Docker to start on boot
sudo systemctl enable docker

# Create systemd service (optional, but recommended)
sudo nano /etc/systemd/system/zoom-mcp.service
```

**Add this content:**
```ini
[Unit]
Description=Zoom MCP Server
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/your-username/apps/zoom-mcp
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

**Enable the service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable zoom-mcp
sudo systemctl start zoom-mcp
```

---

## Step 9: Test the Deployment

### Test Locally on VPS
```bash
curl http://localhost:8080/health
```

### Test from Outside (if using domain)
```bash
curl https://zoom-mcp.yourdomain.com/health
```

---

## Step 10: Configure Gumloop

In Gumloop's "Ask AI" node with remote MCP server:

**Server URL:**
```
https://zoom-mcp.yourdomain.com
```

Or if using IP directly:
```
http://your-vps-ip:8080
```

---

## Maintenance Commands

### View Logs
```bash
docker-compose logs -f zoom-mcp
```

### Restart Server
```bash
docker-compose restart
```

### Stop Server
```bash
docker-compose down
```

### Update Code
```bash
# Pull latest changes (if using Git)
git pull

# Or use rsync from local machine
# rsync -avz --exclude='.venv' /path/to/local/zoom-mcp/ user@vps:~/apps/zoom-mcp/

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

### View Resource Usage
```bash
docker stats zoom-mcp-server
```

### Clean Up Old Images
```bash
docker system prune -a
```

---

## Monitoring (Optional)

### Set Up Log Rotation
```bash
# Edit docker-compose.yml logging section (already configured)
# Logs are limited to 10MB x 3 files
```

### Monitor with Uptime Robot
Sign up at https://uptimerobot.com and add your server URL for monitoring.

### Set Up Alerts
```bash
# Create a simple health check script
nano ~/check-zoom-mcp.sh
```

**Add:**
```bash
#!/bin/bash
if ! curl -f http://localhost:8080/health &> /dev/null; then
    echo "Zoom MCP Server is down!" | mail -s "Alert: Zoom MCP Down" your-email@example.com
    docker-compose -f ~/apps/zoom-mcp/docker-compose.yml restart
fi
```

**Make executable and add to cron:**
```bash
chmod +x ~/check-zoom-mcp.sh
crontab -e
# Add: */5 * * * * /home/your-username/check-zoom-mcp.sh
```

---

## Troubleshooting

### Container Won't Start
```bash
# Check logs
docker-compose logs zoom-mcp

# Check if port is in use
sudo netstat -tlnp | grep 8080

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Can't Connect from Outside
```bash
# Check firewall
sudo ufw status

# Check nginx
sudo nginx -t
sudo systemctl status nginx

# Check if container is running
docker-compose ps
```

### Environment Variables Not Loading
```bash
# Verify .env file exists
cat .env

# Check if Docker Compose is reading it
docker-compose config
```

---

## Security Best Practices

1. **Use HTTPS** - Always use SSL in production
2. **Firewall** - Only open necessary ports
3. **Regular Updates** - Keep Docker and OS updated
4. **Secrets Management** - Never commit .env to Git
5. **Access Control** - Consider adding authentication
6. **Rate Limiting** - Add rate limiting in Nginx
7. **Monitoring** - Set up uptime monitoring
8. **Backups** - Backup your configuration

---

## Quick Reference

### Common Commands
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# Logs
docker-compose logs -f

# Shell access
docker-compose exec zoom-mcp /bin/bash

# Update and restart
git pull && docker-compose down && docker-compose build && docker-compose up -d
```

### File Locations
- **Application:** `~/apps/zoom-mcp`
- **Logs:** `~/apps/zoom-mcp/logs`
- **Nginx Config:** `/etc/nginx/sites-available/zoom-mcp`
- **SSL Certificates:** `/etc/letsencrypt/live/zoom-mcp.yourdomain.com/`

---

## Support

For issues:
1. Check logs: `docker-compose logs -f`
2. Verify environment: `docker-compose config`
3. Test health: `curl http://localhost:8080/health`
4. Check resources: `docker stats`

---

**Last Updated:** October 10, 2025
