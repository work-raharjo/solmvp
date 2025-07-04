# Sol MVP Deployment Guide

This guide provides comprehensive instructions for deploying the Sol MVP (Passport-Based QRIS Wallet) in various environments, from local development to production cloud deployment.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Docker Deployment](#docker-deployment)
4. [Production Deployment](#production-deployment)
5. [Cloud Platform Deployment](#cloud-platform-deployment)
6. [Environment Configuration](#environment-configuration)
7. [Security Considerations](#security-considerations)
8. [Monitoring and Maintenance](#monitoring-and-maintenance)
9. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

**Minimum Requirements:**
- CPU: 2 cores
- RAM: 4GB
- Storage: 20GB SSD
- Network: Stable internet connection

**Recommended for Production:**
- CPU: 4+ cores
- RAM: 8GB+
- Storage: 50GB+ SSD
- Network: High-speed internet with redundancy

### Software Dependencies

- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+
- **Git**: For source code management
- **SSL Certificate**: For HTTPS in production

### External Service Requirements

- **Privy Account**: For KYC verification services
- **Xendit Account**: For payment processing
- **Domain Name**: For production deployment
- **Email Service**: For notifications (optional)

## Local Development Setup

### Quick Start

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd sol_mvp
   ```

2. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start Development Environment**
   ```bash
   docker-compose up -d
   ```

4. **Verify Installation**
   ```bash
   # Check all services are running
   docker-compose ps
   
   # Test API health
   curl http://localhost:5000/api/health
   ```

### Manual Development Setup

If you prefer to run services individually:

#### Backend Setup
```bash
cd backend/sol_backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://sol_user:sol_password@localhost:5432/sol_mvp"
export JWT_SECRET_KEY="your-secret-key"

# Run the application
python src/main.py
```

#### Frontend Setup
```bash
cd frontend/sol_frontend
npm install
npm run dev
```

#### Admin Dashboard Setup
```bash
cd admin_dashboard/sol_admin
npm install
npm run dev
```

#### Database Setup
```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE sol_mvp;
CREATE USER sol_user WITH PASSWORD 'sol_password';
GRANT ALL PRIVILEGES ON DATABASE sol_mvp TO sol_user;
\q

# Run initialization script
psql -U sol_user -d sol_mvp -f database/init.sql
```

## Docker Deployment

### Development Environment

The provided `docker-compose.yml` sets up a complete development environment:

```yaml
# Key services included:
- PostgreSQL database
- Flask backend API
- React frontend
- React admin dashboard
- Redis for caching
```

**Start Development Environment:**
```bash
docker-compose up -d
```

**View Logs:**
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
```

**Stop Environment:**
```bash
docker-compose down
```

### Production Docker Setup

1. **Create Production Environment File**
   ```bash
   cp .env.example .env.production
   # Configure production values
   ```

2. **Build Production Images**
   ```bash
   # Build all images
   docker-compose -f docker-compose.prod.yml build

   # Build specific service
   docker-compose -f docker-compose.prod.yml build backend
   ```

3. **Deploy Production Stack**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Docker Image Management

**Build Custom Images:**
```bash
# Backend
docker build -t sol-backend:latest ./backend/sol_backend

# Frontend
docker build -t sol-frontend:latest ./frontend/sol_frontend

# Admin Dashboard
docker build -t sol-admin:latest ./admin_dashboard/sol_admin
```

**Push to Registry:**
```bash
# Tag for registry
docker tag sol-backend:latest your-registry.com/sol-backend:latest

# Push to registry
docker push your-registry.com/sol-backend:latest
```

## Production Deployment

### Server Preparation

1. **Update System**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install Docker**
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   ```

3. **Install Docker Compose**
   ```bash
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

4. **Configure Firewall**
   ```bash
   sudo ufw allow 22    # SSH
   sudo ufw allow 80    # HTTP
   sudo ufw allow 443   # HTTPS
   sudo ufw enable
   ```

### SSL Certificate Setup

#### Using Let's Encrypt (Recommended)

1. **Install Certbot**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   ```

2. **Obtain Certificate**
   ```bash
   sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
   ```

3. **Auto-renewal Setup**
   ```bash
   sudo crontab -e
   # Add: 0 12 * * * /usr/bin/certbot renew --quiet
   ```

#### Manual Certificate Installation

1. **Create SSL Directory**
   ```bash
   mkdir -p /etc/ssl/certs/sol
   ```

2. **Copy Certificates**
   ```bash
   cp your-certificate.crt /etc/ssl/certs/sol/
   cp your-private-key.key /etc/ssl/certs/sol/
   ```

### Reverse Proxy Setup (Nginx)

1. **Install Nginx**
   ```bash
   sudo apt install nginx
   ```

2. **Configure Nginx**
   ```bash
   sudo nano /etc/nginx/sites-available/sol
   ```

   ```nginx
   server {
       listen 80;
       server_name yourdomain.com www.yourdomain.com;
       return 301 https://$server_name$request_uri;
   }

   server {
       listen 443 ssl http2;
       server_name yourdomain.com www.yourdomain.com;

       ssl_certificate /etc/ssl/certs/sol/certificate.crt;
       ssl_certificate_key /etc/ssl/certs/sol/private.key;

       # Frontend
       location / {
           proxy_pass http://localhost:3000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }

       # Admin Dashboard
       location /admin {
           proxy_pass http://localhost:3001;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }

       # API
       location /api {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

3. **Enable Site**
   ```bash
   sudo ln -s /etc/nginx/sites-available/sol /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

### Database Backup Strategy

1. **Automated Backup Script**
   ```bash
   #!/bin/bash
   # backup.sh
   BACKUP_DIR="/backups/sol"
   DATE=$(date +%Y%m%d_%H%M%S)
   
   mkdir -p $BACKUP_DIR
   
   docker exec sol_database pg_dump -U sol_user sol_mvp > $BACKUP_DIR/sol_backup_$DATE.sql
   
   # Keep only last 7 days
   find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
   ```

2. **Schedule Backups**
   ```bash
   sudo crontab -e
   # Add: 0 2 * * * /path/to/backup.sh
   ```

## Cloud Platform Deployment

### AWS Deployment

#### Using AWS ECS

1. **Create ECS Cluster**
   ```bash
   aws ecs create-cluster --cluster-name sol-cluster
   ```

2. **Create Task Definition**
   ```json
   {
     "family": "sol-backend",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "512",
     "memory": "1024",
     "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
     "containerDefinitions": [
       {
         "name": "sol-backend",
         "image": "your-account.dkr.ecr.region.amazonaws.com/sol-backend:latest",
         "portMappings": [
           {
             "containerPort": 5000,
             "protocol": "tcp"
           }
         ],
         "environment": [
           {
             "name": "DATABASE_URL",
             "value": "postgresql://user:pass@rds-endpoint:5432/sol_mvp"
           }
         ]
       }
     ]
   }
   ```

3. **Create Service**
   ```bash
   aws ecs create-service \
     --cluster sol-cluster \
     --service-name sol-backend-service \
     --task-definition sol-backend \
     --desired-count 2
   ```

#### Using AWS App Runner

1. **Create apprunner.yaml**
   ```yaml
   version: 1.0
   runtime: python3
   build:
     commands:
       build:
         - pip install -r requirements.txt
   run:
     runtime-version: 3.11
     command: python src/main.py
     network:
       port: 5000
       env: PORT
   ```

2. **Deploy via Console or CLI**
   ```bash
   aws apprunner create-service \
     --service-name sol-backend \
     --source-configuration '{
       "ImageRepository": {
         "ImageIdentifier": "your-image-uri",
         "ImageConfiguration": {
           "Port": "5000"
         }
       }
     }'
   ```

### Google Cloud Platform

#### Using Google Cloud Run

1. **Build and Push Image**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT-ID/sol-backend
   ```

2. **Deploy Service**
   ```bash
   gcloud run deploy sol-backend \
     --image gcr.io/PROJECT-ID/sol-backend \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

#### Using Google Kubernetes Engine

1. **Create Cluster**
   ```bash
   gcloud container clusters create sol-cluster \
     --num-nodes=3 \
     --zone=us-central1-a
   ```

2. **Deploy Application**
   ```yaml
   # kubernetes/deployment.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: sol-backend
   spec:
     replicas: 3
     selector:
       matchLabels:
         app: sol-backend
     template:
       metadata:
         labels:
           app: sol-backend
       spec:
         containers:
         - name: sol-backend
           image: gcr.io/PROJECT-ID/sol-backend:latest
           ports:
           - containerPort: 5000
   ```

### Azure Deployment

#### Using Azure Container Instances

```bash
az container create \
  --resource-group sol-rg \
  --name sol-backend \
  --image your-registry.azurecr.io/sol-backend:latest \
  --dns-name-label sol-backend \
  --ports 5000
```

#### Using Azure App Service

```bash
az webapp create \
  --resource-group sol-rg \
  --plan sol-plan \
  --name sol-backend \
  --deployment-container-image-name your-registry.azurecr.io/sol-backend:latest
```

### DigitalOcean App Platform

1. **Create App Spec**
   ```yaml
   # .do/app.yaml
   name: sol-mvp
   services:
   - name: backend
     source_dir: /backend/sol_backend
     github:
       repo: your-username/sol-mvp
       branch: main
     run_command: python src/main.py
     environment_slug: python
     instance_count: 1
     instance_size_slug: basic-xxs
     envs:
     - key: DATABASE_URL
       value: ${db.DATABASE_URL}
   databases:
   - name: db
     engine: PG
     version: "13"
   ```

2. **Deploy**
   ```bash
   doctl apps create .do/app.yaml
   ```

## Environment Configuration

### Environment Variables

Create appropriate `.env` files for each environment:

#### Development (.env.development)
```env
# Database
DATABASE_URL=postgresql://sol_user:sol_password@localhost:5432/sol_mvp

# JWT
JWT_SECRET_KEY=dev-secret-key-change-in-production

# Privy (Sandbox)
PRIVY_API_KEY=privy_sandbox_key
PRIVY_API_URL=https://sandbox-api.privy.id

# Xendit (Test)
XENDIT_API_KEY=xnd_development_key
XENDIT_WEBHOOK_TOKEN=test_webhook_token

# Application
FLASK_ENV=development
DEBUG=true
```

#### Production (.env.production)
```env
# Database
DATABASE_URL=postgresql://user:password@prod-db:5432/sol_mvp

# JWT
JWT_SECRET_KEY=super-secure-production-key-256-bits

# Privy (Production)
PRIVY_API_KEY=privy_production_key
PRIVY_API_URL=https://api.privy.id

# Xendit (Live)
XENDIT_API_KEY=xnd_production_key
XENDIT_WEBHOOK_TOKEN=production_webhook_token

# Application
FLASK_ENV=production
DEBUG=false

# Security
CORS_ORIGINS=https://yourdomain.com,https://admin.yourdomain.com
```

### Configuration Management

#### Using Docker Secrets
```bash
# Create secrets
echo "production_db_password" | docker secret create db_password -
echo "production_jwt_key" | docker secret create jwt_secret -

# Use in docker-compose
services:
  backend:
    secrets:
      - db_password
      - jwt_secret
```

#### Using Environment Files
```bash
# Load environment
docker-compose --env-file .env.production up -d
```

## Security Considerations

### Application Security

1. **Environment Variables**
   - Never commit sensitive data to version control
   - Use strong, unique passwords and API keys
   - Rotate secrets regularly

2. **Database Security**
   ```sql
   -- Create read-only user for monitoring
   CREATE USER monitoring WITH PASSWORD 'secure_password';
   GRANT CONNECT ON DATABASE sol_mvp TO monitoring;
   GRANT USAGE ON SCHEMA public TO monitoring;
   GRANT SELECT ON ALL TABLES IN SCHEMA public TO monitoring;
   ```

3. **API Security**
   - Implement rate limiting
   - Use HTTPS everywhere
   - Validate all inputs
   - Implement proper CORS policies

### Infrastructure Security

1. **Firewall Configuration**
   ```bash
   # Allow only necessary ports
   sudo ufw allow 22/tcp    # SSH
   sudo ufw allow 80/tcp    # HTTP
   sudo ufw allow 443/tcp   # HTTPS
   sudo ufw deny 5432/tcp   # Block direct DB access
   ```

2. **SSH Hardening**
   ```bash
   # Disable password authentication
   sudo nano /etc/ssh/sshd_config
   # Set: PasswordAuthentication no
   # Set: PermitRootLogin no
   sudo systemctl restart ssh
   ```

3. **Docker Security**
   ```bash
   # Run containers as non-root
   USER 1000:1000
   
   # Use read-only filesystems where possible
   docker run --read-only sol-backend
   ```

### Monitoring and Logging

1. **Application Monitoring**
   ```python
   # Add to Flask app
   from flask import request
   import logging
   
   @app.before_request
   def log_request_info():
       logging.info('Request: %s %s', request.method, request.url)
   ```

2. **System Monitoring**
   ```bash
   # Install monitoring tools
   sudo apt install htop iotop nethogs
   
   # Monitor Docker containers
   docker stats
   ```

3. **Log Management**
   ```bash
   # Configure log rotation
   sudo nano /etc/logrotate.d/sol
   ```
   ```
   /var/log/sol/*.log {
       daily
       missingok
       rotate 52
       compress
       delaycompress
       notifempty
       create 644 sol sol
   }
   ```

## Monitoring and Maintenance

### Health Checks

1. **Application Health**
   ```bash
   # API health check
   curl -f http://localhost:5000/api/health || exit 1
   
   # Database connectivity
   docker exec sol_database pg_isready -U sol_user
   ```

2. **Automated Monitoring Script**
   ```bash
   #!/bin/bash
   # monitor.sh
   
   # Check API
   if ! curl -f http://localhost:5000/api/health > /dev/null 2>&1; then
       echo "API is down" | mail -s "Sol API Alert" admin@yourdomain.com
   fi
   
   # Check disk space
   if [ $(df / | tail -1 | awk '{print $5}' | sed 's/%//') -gt 80 ]; then
       echo "Disk space low" | mail -s "Sol Disk Alert" admin@yourdomain.com
   fi
   ```

### Performance Monitoring

1. **Database Performance**
   ```sql
   -- Monitor slow queries
   SELECT query, mean_time, calls 
   FROM pg_stat_statements 
   ORDER BY mean_time DESC 
   LIMIT 10;
   ```

2. **Application Metrics**
   ```python
   # Add Prometheus metrics
   from prometheus_client import Counter, Histogram
   
   REQUEST_COUNT = Counter('requests_total', 'Total requests')
   REQUEST_LATENCY = Histogram('request_duration_seconds', 'Request latency')
   ```

### Backup and Recovery

1. **Database Backup**
   ```bash
   # Full backup
   docker exec sol_database pg_dump -U sol_user sol_mvp > backup.sql
   
   # Incremental backup using WAL-E
   docker run --rm -v postgres_data:/data wal-e backup-push /data
   ```

2. **Application Data Backup**
   ```bash
   # Backup uploaded files
   tar -czf uploads_backup.tar.gz uploads/
   
   # Backup configuration
   tar -czf config_backup.tar.gz .env* docker-compose*.yml
   ```

3. **Recovery Procedures**
   ```bash
   # Restore database
   docker exec -i sol_database psql -U sol_user sol_mvp < backup.sql
   
   # Restore files
   tar -xzf uploads_backup.tar.gz
   ```

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   ```bash
   # Check database status
   docker-compose logs database
   
   # Test connection
   docker exec sol_database psql -U sol_user -d sol_mvp -c "SELECT 1;"
   ```

2. **API Not Responding**
   ```bash
   # Check backend logs
   docker-compose logs backend
   
   # Check if port is bound
   netstat -tlnp | grep 5000
   ```

3. **Frontend Build Issues**
   ```bash
   # Clear npm cache
   npm cache clean --force
   
   # Rebuild node_modules
   rm -rf node_modules package-lock.json
   npm install
   ```

### Performance Issues

1. **High Memory Usage**
   ```bash
   # Monitor memory usage
   docker stats --no-stream
   
   # Increase container memory limits
   docker-compose up -d --scale backend=2
   ```

2. **Slow Database Queries**
   ```sql
   -- Enable query logging
   ALTER SYSTEM SET log_statement = 'all';
   SELECT pg_reload_conf();
   
   -- Analyze slow queries
   EXPLAIN ANALYZE SELECT * FROM transactions WHERE user_id = 1;
   ```

### Debugging Tools

1. **Container Debugging**
   ```bash
   # Access container shell
   docker exec -it sol_backend bash
   
   # View container logs
   docker logs -f sol_backend
   ```

2. **Network Debugging**
   ```bash
   # Test internal connectivity
   docker exec sol_backend ping database
   
   # Check port connectivity
   docker exec sol_backend nc -zv database 5432
   ```

### Recovery Procedures

1. **Service Recovery**
   ```bash
   # Restart specific service
   docker-compose restart backend
   
   # Full stack restart
   docker-compose down && docker-compose up -d
   ```

2. **Data Recovery**
   ```bash
   # Restore from backup
   docker exec -i sol_database psql -U sol_user sol_mvp < latest_backup.sql
   
   # Verify data integrity
   docker exec sol_database psql -U sol_user -d sol_mvp -c "SELECT COUNT(*) FROM users;"
   ```

---

This deployment guide provides comprehensive instructions for deploying Sol MVP in various environments. For additional support or specific deployment scenarios, please contact the development team.

