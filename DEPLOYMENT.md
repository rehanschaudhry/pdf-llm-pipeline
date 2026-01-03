# Deployment Guide

## Local Development

See [QUICKSTART.md](QUICKSTART.md) for local setup.

## Production Deployment

### Prerequisites

- Ubuntu 20.04+ or similar Linux server
- Docker & Docker Compose
- Python 3.11+
- Domain name (optional)
- SSL certificate (optional, recommended)

### Option 1: Docker Deployment (Recommended)

#### 1. Create Production Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ ./src/
COPY credentials.json .
COPY docker-compose.yml .

# Expose port
EXPOSE 5000

# Run with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "src.app.flask_app:app"]
```

#### 2. Update docker-compose.yml for Production
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: pdf_pipeline_postgres
    environment:
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=${DB_NAME}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

  app:
    build: .
    container_name: pdf_pipeline_api
    environment:
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
      - FLASK_ENV=production
    ports:
      - "5000:5000"
    depends_on:
      - postgres
    restart: always
    volumes:
      - ./credentials.json:/app/credentials.json:ro
      - ./token.json:/app/token.json

volumes:
  postgres_data:
```

#### 3. Environment Variables

Create `.env` file:
```env
DB_USER=pdfuser
DB_PASSWORD=your_secure_password_here
DB_NAME=pdf_pipeline
FLASK_ENV=production
SECRET_KEY=your_secret_key_here
```

#### 4. Deploy
```bash
# Build and start
docker-compose up -d --build

# Check logs
docker-compose logs -f app

# Check status
docker-compose ps
```

### Option 2: Traditional Server Deployment

#### 1. Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Install nginx (reverse proxy)
sudo apt install nginx -y
```

#### 2. Application Setup
```bash
# Clone repository
git clone <your-repo>
cd pdf_pipeline_project

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn  # Production WSGI server

# Setup PostgreSQL
sudo -u postgres createuser pdfuser
sudo -u postgres createdb pdf_pipeline
sudo -u postgres psql -c "ALTER USER pdfuser WITH PASSWORD 'secure_password';"

# Create tables
python -m src.app.create_table
```

#### 3. Run with Gunicorn
```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 src.app.flask_app:app
```

#### 4. Setup as System Service

Create `/etc/systemd/system/pdf-pipeline.service`:
```ini
[Unit]
Description=PDF Pipeline API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/pdf_pipeline_project
Environment="PATH=/home/ubuntu/pdf_pipeline_project/venv/bin"
ExecStart=/home/ubuntu/pdf_pipeline_project/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 src.app.flask_app:app

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable pdf-pipeline
sudo systemctl start pdf-pipeline
sudo systemctl status pdf-pipeline
```

#### 5. Nginx Reverse Proxy

Create `/etc/nginx/sites-available/pdf-pipeline`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # File upload size limit
        client_max_body_size 50M;
    }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/pdf-pipeline /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### SSL/HTTPS (Recommended)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

## Cloud Platform Deployment

### AWS

1. **EC2**: Launch Ubuntu instance
2. **RDS**: PostgreSQL database
3. **S3**: Alternative to Google Drive
4. **Load Balancer**: For high availability

### Google Cloud Platform

1. **Compute Engine**: VM instance
2. **Cloud SQL**: PostgreSQL
3. **Cloud Storage**: Alternative storage
4. **Load Balancer**: Traffic distribution

### Azure

1. **Virtual Machine**: Ubuntu VM
2. **Azure Database**: PostgreSQL
3. **Blob Storage**: Alternative storage
4. **Application Gateway**: Load balancing

## Monitoring

### Application Logs
```bash
# View logs
tail -f pipeline.log

# Docker logs
docker-compose logs -f app
```

### Database Monitoring
```bash
# Connect to PostgreSQL
docker exec -it pdf_pipeline_postgres psql -U pdfuser -d pdf_pipeline

# Check document counts
SELECT status, COUNT(*) FROM documents GROUP BY status;

# Check recent uploads
SELECT filename, status, created_at 
FROM documents 
ORDER BY created_at DESC 
LIMIT 10;
```

## Backup & Recovery

### Database Backup
```bash
# Backup
docker exec pdf_pipeline_postgres pg_dump -U pdfuser pdf_pipeline > backup.sql

# Restore
docker exec -i pdf_pipeline_postgres psql -U pdfuser pdf_pipeline < backup.sql
```

### Google Drive Backup

Files are already in Google Drive (cloud backup).

## Security Checklist

- [ ] Change default passwords
- [ ] Use environment variables for secrets
- [ ] Enable HTTPS/SSL
- [ ] Setup firewall (UFW)
- [ ] Regular security updates
- [ ] Implement rate limiting
- [ ] Add API authentication
- [ ] Setup monitoring/alerts
- [ ] Regular backups
- [ ] Restrict Google OAuth scopes

## Performance Tuning

### Flask

- Use Gunicorn with multiple workers
- Enable gzip compression
- Implement caching (Redis)

### PostgreSQL

- Tune shared_buffers
- Enable connection pooling
- Create indexes on frequently queried columns
- Regular VACUUM

### Google Drive

- Batch API requests
- Implement retry logic
- Use exponential backoff

## Troubleshooting

See [README.md](README.md#troubleshooting) for common issues.