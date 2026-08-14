# Production Deployment Guide
## Enterprise University Management Platform (EUMP)
### Item 76: Complete Deployment Strategy

---

## Table of Contents
1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Infrastructure Requirements](#infrastructure-requirements)
3. [Database Setup](#database-setup)
4. [Application Configuration](#application-configuration)
5. [Deployment Procedures](#deployment-procedures)
6. [Post-Deployment Validation](#post-deployment-validation)
7. [Monitoring & Alerting](#monitoring--alerting)
8. [Backup & Disaster Recovery](#backup--disaster-recovery)
9. [Performance Tuning](#performance-tuning)
10. [Security Hardening](#security-hardening)

---

## Pre-Deployment Checklist

### Code Quality
- [ ] All tests passing (pytest backend tests)
- [ ] No compilation errors in frontend (TypeScript)
- [ ] Code review completed
- [ ] Security scan passed (OWASP, dependency audit)
- [ ] API documentation generated (Swagger/OpenAPI)

### Environment Setup
- [ ] Production environment variables configured
- [ ] Secrets stored in secure vault (not in git)
- [ ] SSL/TLS certificates prepared
- [ ] Domain DNS configured
- [ ] Email service configured for notifications

### Team Preparation
- [ ] Deployment runbook reviewed
- [ ] Rollback procedures documented
- [ ] On-call rotation established
- [ ] Communication channels set up
- [ ] Stakeholders notified of deployment window

---

## Infrastructure Requirements

### Minimum Hardware Specifications

#### Web Servers (Application)
```
CPU: 4+ cores
RAM: 8 GB minimum (16 GB recommended for 1,000+ concurrent users)
Storage: 100 GB SSD for application
OS: Ubuntu 20.04 LTS or equivalent
```

#### Database Servers (MongoDB)
```
CPU: 8+ cores for production
RAM: 16 GB minimum (32 GB for large deployments)
Storage: 500 GB SSD (adjust based on expected data volume)
Replication: 3-node replica set for HA
Backup: Separate backup instance
```

#### Cache Layer (Redis - Optional)
```
CPU: 2+ cores
RAM: 4-8 GB
Storage: 20 GB SSD
Purpose: Session caching, rate limiting
```

### Recommended Deployment Architecture

```
                        ┌─────────────────┐
                        │   Load Balancer │
                        │   (NGinX/HAProxy)
                        └────────┬────────┘
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
            ┌───▼────┐       ┌───▼────┐       ┌──▼────┐
            │  App1   │       │  App2   │       │ App3  │
            │ FastAPI │       │ FastAPI │       │FastAPI│
            └────┬────┘       └────┬────┘       └───┬───┘
                 │                │                  │
                 └────────────────┼──────────────────┘
                                  │
                        ┌─────────▼────────┐
                        │ MongoDB Replica  │
                        │ Set (3-node)     │
                        └──────────────────┘
                                  │
                 ┌────────────────┴───────────────┐
                 │                                │
         ┌───────▼────────┐           ┌──────────▼──────┐
         │  Backup Node   │           │  Analytics DB   │
         │  (Read-only)   │           │  (Archival)     │
         └────────────────┘           └─────────────────┘
```

---

## Database Setup

### MongoDB Configuration

#### 1. Replica Set Initialization

```bash
# On primary node
mongosh

# Enter replica set configuration
rs.initiate({
  _id: "eump-primary",
  members: [
    { _id: 0, host: "mongo-primary:27017" },
    { _id: 1, host: "mongo-secondary1:27017" },
    { _id: 2, host: "mongo-secondary2:27017" }
  ]
})

# Verify status
rs.status()
```

#### 2. Authentication Setup

```javascript
// Create admin user
db.createUser({
  user: "admin",
  pwd: "STRONG_PASSWORD",
  roles: ["root"]
})

// Create application user
use eump_db
db.createUser({
  user: "eump_app",
  pwd: "APP_DB_PASSWORD",
  roles: [
    { role: "readWrite", db: "eump_db" },
    { role: "dbAdmin", db: "eump_db" }
  ]
})

// Create backup user (read-only)
db.createUser({
  user: "eump_backup",
  pwd: "BACKUP_PASSWORD",
  roles: [
    { role: "backup", db: "admin" },
    { role: "read", db: "eump_db" }
  ]
})
```

#### 3. Index Creation (Beanie handles most)

```javascript
// Critical indexes for high-volume operations
db.student_fees.createIndex({ tenant_id: 1, student_id: 1 })
db.payment_records.createIndex({ tenant_id: 1, payment_date: -1 })
db.attendance_records.createIndex({ tenant_id: 1, course_id: 1, date: -1 })
db.course_grades.createIndex({ tenant_id: 1, status: 1 })
db.application_workflow_states.createIndex({ tenant_id: 1, current_status: 1 })

// Enable compression for large collections
db.student_academic_records.createIndex({ tenant_id: 1, cgpa: -1 })
```

#### 4. Backup Configuration

```bash
# Automated daily backup script
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mongodump --uri="mongodb://eump_backup:PASSWORD@mongo-primary:27017/eump_db" \
  --out=/backups/eump_${TIMESTAMP} \
  --gzip

# Retention: Keep 30 days of backups
find /backups -name "eump_*" -type d -mtime +30 -exec rm -rf {} \;
```

---

## Application Configuration

### 1. Environment Variables

Create `.env.production`:

```env
# Core Settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Database
MONGODB_URL=mongodb+srv://eump_app:PASSWORD@mongo-cluster/eump_db?replicaSet=eump-primary&authSource=admin
MONGODB_MAX_POOL_SIZE=50
MONGODB_TIMEOUT=10000

# JWT & Security
SECRET_KEY=PRODUCTION_SECRET_KEY_MIN_32_CHARS
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
REFRESH_TOKEN_EXPIRATION_DAYS=7

# CORS
ALLOWED_ORIGINS=https://app.university.edu,https://www.university.edu
ALLOWED_METHODS=GET,POST,PUT,DELETE,PATCH,OPTIONS
ALLOWED_HEADERS=*

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=noreply@university.edu
MAIL_PASSWORD=EMAIL_APP_PASSWORD
MAIL_FROM=EUMP <noreply@university.edu>
MAIL_USE_TLS=true

# Paystack Integration (for payments)
PAYSTACK_PUBLIC_KEY=pk_live_xxxxx
PAYSTACK_SECRET_KEY=sk_live_xxxxx

# AWS S3 (for document storage)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_S3_BUCKET=eump-documents
AWS_S3_REGION=us-east-1

# Redis (optional, for caching)
REDIS_URL=redis://redis-cache:6379

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_HOUR=1000
RATE_LIMIT_BURST=50

# Analytics
ANALYTICS_ENABLED=true
ANALYTICS_RETENTION_DAYS=90

# Archival
ARCHIVAL_ENABLED=true
ARCHIVAL_SCHEDULE=0 2 * * *  # 2 AM daily
```

### 2. Gunicorn/Uvicorn Configuration

Create `gunicorn_config.py`:

```python
# Gunicorn configuration for production
bind = "0.0.0.0:8000"
workers = 4  # CPU cores * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 5
accesslog = "/var/log/eump/access.log"
errorlog = "/var/log/eump/error.log"
loglevel = "info"

# Performance
preload_app = True  # Pre-load application in master process
worker_connections = 1000
```

### 3. Nginx Configuration

Create `/etc/nginx/sites-available/eump`:

```nginx
upstream app_servers {
    server app1:8000;
    server app2:8000;
    server app3:8000;
}

server {
    listen 80;
    server_name app.university.edu;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name app.university.edu;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/app.university.edu/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.university.edu/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Proxy configuration
    location / {
        proxy_pass http://app_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    # Static files
    location /static/ {
        alias /app/static/;
        expires 1y;
    }

    # API rate limiting
    location /api/ {
        limit_req zone=api burst=50 nodelay;
        proxy_pass http://app_servers;
    }
}

# Rate limiting zone definition
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
```

---

## Deployment Procedures

### Step 1: Pre-Deployment Tasks

```bash
# 1. Code deployment
git pull origin main
git tag -a v1.0.0-prod -m "Production release"
git push origin v1.0.0-prod

# 2. Run database migrations
cd backend
python -m alembic upgrade head

# 3. Create indexes
python scripts/create_indexes.py

# 4. Build frontend
cd ../frontend
npm run build
npm run build:ssr  # Server-side rendering if applicable
```

### Step 2: Blue-Green Deployment

```bash
# Start new instances (Green)
docker-compose -f docker-compose.prod.yml up -d app-green

# Wait for health checks
./scripts/wait-for-health.sh app-green:8000 300

# Run smoke tests
pytest tests/smoke/ --target=app-green:8000

# Switch traffic (Blue → Green)
./scripts/switch-load-balancer.sh app-green

# Keep Blue running for quick rollback
```

### Step 3: Post-Deployment

```bash
# 1. Verify all services
curl https://app.university.edu/api/v1/health

# 2. Check database connections
python -c "from app.infrastructure.database.connection import init_db; await init_db()"

# 3. Verify index creation
mongosh eump_db --eval "db.currentOp(true)"

# 4. Monitor logs
tail -f /var/log/eump/error.log
tail -f /var/log/eump/access.log
```

---

## Post-Deployment Validation

### Health Checks

```bash
# Application health
curl https://app.university.edu/health

# Database connectivity
python scripts/validate_db.py

# API endpoints sampling
pytest tests/smoke/test_critical_endpoints.py

# Performance baseline
ab -n 1000 -c 100 https://app.university.edu/api/v1/health
```

### Data Verification

```bash
# Verify all collections created
mongo eump_db << EOF
show collections
db.student_academic_records.estimatedDocumentCount()
db.application_workflow_states.estimatedDocumentCount()
db.payment_records.estimatedDocumentCount()
EOF

# Check indexes
mongo eump_db << EOF
db.student_fees.getIndexes()
db.payment_records.getIndexes()
EOF
```

---

## Monitoring & Alerting

### Prometheus Metrics (Add to app)

```python
# In app/main.py
from prometheus_client import Counter, Histogram
from starlette_prometheus import PrometheusMiddleware, handle_metrics

app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", handle_metrics)

# Custom metrics
request_count = Counter('eump_requests_total', 'Total requests', ['method', 'endpoint'])
response_time = Histogram('eump_response_time_seconds', 'Response time', ['endpoint'])
```

### Grafana Dashboards

Create dashboards for:
- Request rate and response time (by endpoint)
- Error rate and types
- Database connection pool usage
- Memory and CPU usage
- MongoDB replication lag
- Payment processing success rate

### Alert Rules (Prometheus)

```yaml
groups:
  - name: eump_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(eump_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        annotations:
          summary: "High error rate detected"

      - alert: HighLatency
        expr: histogram_quantile(0.95, eump_response_time_seconds) > 1
        for: 5m
        annotations:
          summary: "P95 latency > 1s"

      - alert: DatabaseDown
        expr: mongodb_up == 0
        for: 1m
        annotations:
          summary: "MongoDB replica set member down"
```

---

## Backup & Disaster Recovery

### Automated Backup Strategy

```bash
#!/bin/bash
# Daily full backup + incremental backups
BACKUP_PATH="/backups/eump"
RETENTION_DAYS=30

# Full backup (Monday)
if [ $(date +%A) = "Monday" ]; then
    mongodump --uri="mongodb://..." \
        --out=$BACKUP_PATH/full_$(date +%Y%m%d) \
        --gzip
fi

# Incremental backup (other days)
mongodump --uri="mongodb://..." \
    --out=$BACKUP_PATH/incr_$(date +%Y%m%d) \
    --query='{"createdAt": {$gte: new Date(Date.now() - 24*60*60*1000)}}' \
    --gzip

# Cleanup old backups
find $BACKUP_PATH -type d -mtime +$RETENTION_DAYS -exec rm -rf {} \;
```

### Recovery Procedure

```bash
# 1. Stop application
systemctl stop eump

# 2. Backup current data
mongodump --out=/backups/pre_restore_$(date +%s)

# 3. Restore from backup
mongorestore --uri="mongodb://..." /backups/full_20240814

# 4. Verify data integrity
python scripts/validate_data_integrity.py

# 5. Restart application
systemctl start eump
```

### RTO/RPO Targets

- **RTO (Recovery Time Objective):** 1 hour
- **RPO (Recovery Point Objective):** 4 hours
- **Backup Frequency:** Every 4 hours
- **Retention Period:** 30 days

---

## Performance Tuning

### MongoDB Optimization

```javascript
// Connection pooling
db.adminCommand({
  configureFailPoint: "setConnectionPoolWaitQueue",
  mode: "off"
})

// Query profiling for slow queries
db.setProfilingLevel(1, { slowms: 100 })

// Check slow queries
db.system.profile.find({ millis: { $gt: 100 } }).sort({ ts: -1 }).limit(10)
```

### Application Optimization

```python
# In app/config.py
# Connection pooling
MONGODB_MAX_POOL_SIZE = 50
MONGODB_MIN_POOL_SIZE = 10

# Caching
CACHE_TTL = 300  # 5 minutes
CACHE_MAX_SIZE = 10000

# Pagination defaults
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
```

### FastAPI Performance

```python
# Add caching middleware
from fastapi_cache2 import FastAPICache2
from fastapi_cache2.backends.redis import RedisBackend
from redis import asyncio as aioredis

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache2.init(RedisBackend(redis), prefix="eump")
```

---

## Security Hardening

### 1. Network Security

```bash
# UFW firewall rules
ufw default deny incoming
ufw default allow outgoing
ufw allow 443/tcp   # HTTPS
ufw allow 22/tcp    # SSH (from specific IPs only)
ufw allow 27017/tcp # MongoDB (from app servers only)
ufw enable
```

### 2. Data Protection

```python
# In requirements.txt
cryptography>=41.0.0  # For encryption
python-jose>=3.3.0   # JWT signing
bcrypt>=4.0.0        # Password hashing
```

### 3. Secret Management

```bash
# Use HashiCorp Vault or AWS Secrets Manager
# Never store secrets in environment variables on production
vault kv put secret/eump/db \
  url="mongodb+srv://..." \
  password="..."
```

### 4. API Security

```python
# Rate limiting
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/v1/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, credentials: Credentials):
    pass

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.university.edu"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)
```

### 5. Logging & Audit

```python
# Centralized logging to ELK stack
import logging
from pythonjsonlogger import jsonlogger

handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)

# All database operations logged
logger.info({
    "event": "db_query",
    "user_id": user_id,
    "collection": collection_name,
    "operation": "insert",
    "timestamp": datetime.utcnow(),
})
```

---

## Rollback Procedure

If critical issues occur post-deployment:

```bash
# 1. Alert team and stakeholders
# 2. Immediate rollback
./scripts/switch-load-balancer.sh app-blue

# 3. Investigate issue
grep -A 10 "ERROR" /var/log/eump/error.log

# 4. Fix and retest
git revert COMMIT_HASH
pytest tests/smoke/ --target=app-blue:8000

# 5. Schedule re-deployment for next window
```

---

## Maintenance Windows

**Scheduled Maintenance:** Every Sunday, 2:00 AM - 4:00 AM UTC

- Database optimization and index rebuilds
- Backup verification and restore testing
- Log rotation and archival
- Security patches
- Performance baseline measurement

---

## Disaster Recovery Contact List

- **On-Call Engineer:** +1-XXX-XXX-XXXX
- **Database Admin:** +1-XXX-XXX-XXXX
- **Security Lead:** +1-XXX-XXX-XXXX
- **Incident Channel:** #eump-incidents on Slack

---

**Document Version:** 1.0  
**Last Updated:** 2026-08-14  
**Next Review:** 2026-12-14
