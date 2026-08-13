# Enterprise University Management Platform - Deployment Guide

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Backend Deployment](#backend-deployment)
4. [Frontend Deployment](#frontend-deployment)
5. [Database Setup](#database-setup)
6. [Security Configuration](#security-configuration)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Backend Requirements
- **Python**: 3.10+
- **FastAPI**: 0.104.1+
- **MongoDB**: 5.0+ (Atlas or self-hosted)
- **Redis**: 6.0+ (optional, for caching/sessions)
- **OS**: Linux (Ubuntu 20.04+), macOS, or Windows Server 2019+

### Frontend Requirements
- **Node.js**: 18+
- **npm**: 9+
- **Modern Browser**: Chrome 90+, Firefox 88+, Safari 14+

### Server Specifications
- **CPU**: 4+ cores recommended
- **RAM**: 8GB minimum (16GB recommended)
- **Storage**: 100GB+ SSD
- **Network**: Minimum 100 Mbps connection

---

## Pre-Deployment Checklist

### Backend Checklist
- [ ] Python 3.10+ installed
- [ ] All dependencies in requirements.txt resolved
- [ ] Environment variables configured (.env file created)
- [ ] Database connection tested
- [ ] Redis connection tested (if enabled)
- [ ] JWT secret keys generated
- [ ] All tests passing (`pytest`)
- [ ] Code quality check passing (`flake8`, `pylint`)
- [ ] Security scan completed (`bandit`)

### Frontend Checklist
- [ ] Node.js 18+ installed
- [ ] All npm dependencies installed
- [ ] Environment variables in .env.production
- [ ] API endpoint URLs configured
- [ ] Build completes without errors (`npm run build`)
- [ ] No TypeScript errors (`tsc --noEmit`)
- [ ] All tests passing (`npm run test`)

### Infrastructure Checklist
- [ ] SSL/TLS certificates obtained (Let's Encrypt recommended)
- [ ] Firewall rules configured
- [ ] Load balancer configured
- [ ] Backup strategy established
- [ ] Monitoring setup prepared
- [ ] Domain names configured
- [ ] CDN configured (optional)

---

## Backend Deployment

### Step 1: Prepare Environment

```bash
# Clone repository
git clone https://github.com/yourorgan/eump.git
cd eump/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with production values
```

### Step 2: Environment Variables

Create `.env` with the following:

```env
# Environment
ENVIRONMENT=production
DEBUG=false

# Database
MONGODB_URL=mongodb+srv://user:password@cluster.mongodb.net/eump_prod
DATABASE_NAME=eump_prod

# JWT
JWT_SECRET_KEY=your-super-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
JWT_REFRESH_EXPIRATION_DAYS=30

# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
API_RELOAD=false

# CORS
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Email (for notifications)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SENDER_EMAIL=noreply@yourdomain.com

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# AWS S3 (for file storage)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_S3_BUCKET=eump-prod-bucket
AWS_REGION=us-east-1

# Sentry (error tracking)
SENTRY_DSN=your-sentry-dsn

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Step 3: Database Setup

```bash
# Run database migrations/initialization
python scripts/init_db.py

# Create initial admin user
python scripts/create_admin.py --email admin@university.edu --password SecurePass123!

# Seed reference data (optional)
python scripts/seed_data.py
```

### Step 4: Run Tests

```bash
# Unit tests
pytest tests/ -v

# Integration tests
pytest tests/ -v --markers=integration

# Coverage report
pytest tests/ --cov=app --cov-report=html
```

### Step 5: Build & Deploy

#### Option A: Docker Deployment (Recommended)

```bash
# Build Docker image
docker build -t eump-backend:1.0.0 .

# Run container
docker run -d \
  --name eump-backend \
  --env-file .env \
  -p 8000:8000 \
  -v /var/log/eump:/app/logs \
  eump-backend:1.0.0

# View logs
docker logs -f eump-backend
```

#### Option B: Systemd Service Deployment

Create `/etc/systemd/system/eump-backend.service`:

```ini
[Unit]
Description=EUMP Backend Service
After=network.target

[Service]
Type=notify
User=eump
WorkingDirectory=/opt/eump/backend
Environment="PATH=/opt/eump/backend/venv/bin"
EnvironmentFile=/opt/eump/backend/.env
ExecStart=/opt/eump/backend/venv/bin/gunicorn \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  app.main:app
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable eump-backend
sudo systemctl start eump-backend
sudo systemctl status eump-backend
```

#### Option C: Manual Deployment with Uvicorn

```bash
# Install production server
pip install gunicorn uvicorn[standard]

# Run with Gunicorn + Uvicorn workers
gunicorn -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 app.main:app
```

### Step 6: Nginx Reverse Proxy

Create `/etc/nginx/sites-available/eump`:

```nginx
upstream eump_backend {
    server localhost:8000;
    server localhost:8001;
    server localhost:8002;
    server localhost:8003;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
    gzip_min_length 1000;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/s;
    limit_req zone=api_limit burst=200 nodelay;

    location / {
        proxy_pass http://eump_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # API documentation
    location /docs {
        proxy_pass http://eump_backend;
        auth_basic "EUMP API Documentation";
        auth_basic_user_file /etc/nginx/.htpasswd;
    }

    # Health check endpoint (public)
    location /health {
        proxy_pass http://eump_backend;
        access_log off;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

Enable Nginx site:
```bash
sudo ln -s /etc/nginx/sites-available/eump /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Frontend Deployment

### Step 1: Build for Production

```bash
cd frontend

# Install dependencies
npm install

# Build
npm run build

# Output: dist/ folder with optimized bundles
```

### Step 2: Deploy to CDN

#### Option A: AWS CloudFront + S3

```bash
# Upload build artifacts to S3
aws s3 sync dist/ s3://eump-frontend-prod --delete

# Invalidate CloudFront distribution
aws cloudfront create-invalidation --distribution-id E1234567890ABC --paths "/*"
```

#### Option B: Netlify

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
netlify deploy --prod --dir=dist
```

#### Option C: Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

#### Option D: Self-Hosted (Nginx)

```bash
# Copy build to web server
scp -r dist/* user@server:/var/www/eump-app/

# Configure Nginx
sudo vi /etc/nginx/sites-available/eump-frontend
```

Nginx configuration:

```nginx
server {
    listen 443 ssl http2;
    server_name app.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/app.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.yourdomain.com/privkey.pem;

    root /var/www/eump-app;
    index index.html;

    # Cache control
    location ~* \.(js|css|png|jpg|jpeg|gif|ico)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # SPA routing - always serve index.html for non-file routes
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api/ {
        proxy_pass https://api.yourdomain.com;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name app.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

---

## Database Setup

### MongoDB Atlas (Cloud)

1. Create account at https://www.mongodb.com/cloud/atlas
2. Create project and cluster
3. Configure IP whitelist (add your server IP)
4. Create database user
5. Get connection string
6. Set `MONGODB_URL` in .env

### Self-Hosted MongoDB

```bash
# Install MongoDB
sudo apt-get install -y mongodb-org

# Start service
sudo systemctl start mongod
sudo systemctl enable mongod

# Connect to mongo
mongosh

# Create database and user
use eump_prod
db.createUser({
  user: "eump_user",
  pwd: "SecurePassword123",
  roles: ["readWrite", "dbAdmin"]
})
```

### Database Backup

Create `/opt/eump/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/eump"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/eump_backup_$TIMESTAMP.tar.gz"

# Backup MongoDB
mongodump --uri="mongodb+srv://user:pass@cluster.mongodb.net/eump_prod" \
  --archive="$BACKUP_FILE" --gzip

# Upload to S3
aws s3 cp "$BACKUP_FILE" s3://eump-backups/

# Keep only last 30 days
find $BACKUP_DIR -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE"
```

Schedule with cron:
```bash
0 2 * * * /opt/eump/backup.sh  # Daily at 2 AM
```

---

## Security Configuration

### SSL/TLS Certificates

Use Let's Encrypt for free SSL:

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot certonly --nginx -d api.yourdomain.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### Firewall Rules

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### Security Headers

Add to Nginx:

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' https: data: 'unsafe-inline'" always;
```

### API Key Management

```python
# Generate secure key
from secrets import token_urlsafe
key = token_urlsafe(32)
print(key)
```

---

## Monitoring & Maintenance

### Application Monitoring

```bash
# Install Prometheus
sudo apt-get install prometheus

# Install Grafana
sudo apt-get install grafana-server

# Configure Prometheus to scrape /metrics endpoint
```

### Log Aggregation

```bash
# Install ELK Stack
docker-compose -f elk-docker-compose.yml up -d

# Configure application to send logs to ELK
```

### Health Checks

```bash
# Regular health check
curl https://api.yourdomain.com/health

# Expected response:
# {"status": "ok", "environment": "production"}
```

### Performance Monitoring

- Monitor API response times
- Track database query times
- Monitor CPU and memory usage
- Track active connections
- Monitor disk space

---

## Troubleshooting

### Backend Issues

#### Connection Timeout
```bash
# Check if service is running
sudo systemctl status eump-backend

# Check logs
journalctl -u eump-backend -n 50

# Verify database connection
python -c "from app.infrastructure.database.connection import init_db; asyncio.run(init_db())"
```

#### High Memory Usage
```bash
# Check process memory
ps aux | grep gunicorn

# Restart service
sudo systemctl restart eump-backend

# Increase worker timeout
# Edit /etc/systemd/system/eump-backend.service
# Change: TimeoutStopSec=300
```

### Frontend Issues

#### Build Errors
```bash
# Clear node_modules and rebuild
rm -rf node_modules package-lock.json
npm install
npm run build
```

#### Runtime Errors
- Check browser console for errors
- Check network tab for failed requests
- Verify API endpoint is correct
- Check JWT token validity

### Database Issues

#### Connection Failures
```bash
# Test MongoDB connection
mongosh --uri="mongodb+srv://user:pass@cluster.mongodb.net/eump_prod"

# Check MongoDB status
sudo systemctl status mongod

# View MongoDB logs
sudo tail -f /var/log/mongodb/mongod.log
```

#### Performance Issues
```bash
# Check slow queries
db.setProfilingLevel(1, { slowms: 100 })

# Analyze queries
db.system.profile.find().limit(5).sort({ ts : -1 }).pretty()
```

---

## Post-Deployment

### Verification Checklist

- [ ] Backend API responding on /health
- [ ] Frontend loads without errors
- [ ] Login functionality works
- [ ] Dashboard displays correctly
- [ ] API documentation accessible at /docs
- [ ] SSL certificate valid
- [ ] Monitoring dashboards showing data
- [ ] Backups running successfully
- [ ] Email notifications configured
- [ ] Error tracking (Sentry) operational

### Performance Tuning

- Configure nginx caching headers
- Enable gzip compression
- Optimize MongoDB indexes
- Configure CDN caching
- Implement rate limiting

### Maintenance Schedule

- **Weekly**: Monitor system resources and logs
- **Monthly**: Review and optimize database performance
- **Quarterly**: Security audit and dependency updates
- **Annually**: Full system review and capacity planning

---

## Support & Escalation

For deployment issues:
1. Check logs: `journalctl -u eump-backend -n 100`
2. Verify configuration: Review .env file
3. Test connectivity: `curl https://api.yourdomain.com/health`
4. Contact support: api-support@yourdomain.com

---

**Deployment Guide Version**: 1.0.0  
**Last Updated**: 2026-08-13  
**Next Review**: 2026-09-13
