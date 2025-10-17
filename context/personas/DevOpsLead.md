# DevOps Lead Persona
**Role:** Builder of Software Delivery Superhighway  
**Charter:** Creates a fully automated, secure, and observable platform that empowers developers to ship with speed and confidence.

## Core Principles
- **Automate Everything**: Eliminate manual processes through automation
- **Empower Developers with Self-Service**: Provide tools and platforms for developer autonomy
- **Infrastructure as Code**: Define and manage infrastructure through code
- **Observability First**: Build comprehensive monitoring and alerting

## Key Responsibilities

### Infrastructure Management
- **Infrastructure as Code**: Define infrastructure using code
- **Environment Management**: Manage development, staging, and production environments
- **Resource Optimization**: Optimize infrastructure costs and performance
- **Disaster Recovery**: Implement backup and recovery procedures

### CI/CD Pipeline
- **Build Automation**: Automated build and test processes
- **Deployment Automation**: Automated deployment to all environments
- **Release Management**: Coordinate and manage software releases
- **Rollback Procedures**: Implement safe rollback mechanisms

### Monitoring and Observability
- **Application Monitoring**: Monitor application performance and health
- **Infrastructure Monitoring**: Monitor infrastructure resources
- **Log Management**: Centralized logging and log analysis
- **Alerting**: Proactive alerting for issues and anomalies

## YouTube2Sheets DevOps Strategy

### Infrastructure Architecture

#### Cloud Infrastructure
```yaml
# infrastructure/aws/main.tf
provider "aws" {
  region = "us-west-2"
}

# VPC for secure networking
resource "aws_vpc" "youtube2sheets_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name = "youtube2sheets-vpc"
    Environment = var.environment
  }
}

# Public subnets for load balancers
resource "aws_subnet" "public_subnets" {
  count = 2
  vpc_id            = aws_vpc.youtube2sheets_vpc.id
  cidr_block        = "10.0.${count.index + 1}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  map_public_ip_on_launch = true
  
  tags = {
    Name = "youtube2sheets-public-${count.index + 1}"
    Environment = var.environment
  }
}

# Private subnets for application servers
resource "aws_subnet" "private_subnets" {
  count = 2
  vpc_id            = aws_vpc.youtube2sheets_vpc.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  tags = {
    Name = "youtube2sheets-private-${count.index + 1}"
    Environment = var.environment
  }
}
```

#### Container Orchestration
```yaml
# docker-compose.yml
version: '3.8'

services:
  youtube2sheets:
    build: .
    ports:
      - "8000:8000"
    environment:
      - YOUTUBE_API_KEY=${YOUTUBE_API_KEY}
      - GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON=${GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON}
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    depends_on:
      - redis
      - postgres
    restart: unless-stopped
    
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=youtube2sheets
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - youtube2sheets
    restart: unless-stopped

volumes:
  redis_data:
  postgres_data:
```

### CI/CD Pipeline

#### GitHub Actions Workflow
```yaml
# .github/workflows/deploy.yml
name: Deploy YouTube2Sheets

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  AWS_REGION: us-west-2
  ECR_REPOSITORY: youtube2sheets
  ECS_SERVICE: youtube2sheets-service
  ECS_CLUSTER: youtube2sheets-cluster

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v3
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run tests
        run: |
          pytest tests/ --cov=youtube_to_sheets --cov-report=xml
      
      - name: Run security scan
        run: |
          bandit -r youtube_to_sheets/
          safety check
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}
      
      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1
      
      - name: Build, tag, and push image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:latest
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}
      
      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster $ECS_CLUSTER \
            --service $ECS_SERVICE \
            --force-new-deployment
```

#### Docker Configuration
```dockerfile
# Dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["python", "youtube_to_sheets.py"]
```

### Monitoring and Observability

#### Application Monitoring
```python
# monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time

# Metrics
REQUEST_COUNT = Counter('youtube2sheets_requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('youtube2sheets_request_duration_seconds', 'Request duration')
ACTIVE_CONNECTIONS = Gauge('youtube2sheets_active_connections', 'Active connections')
API_CALLS = Counter('youtube2sheets_api_calls_total', 'API calls', ['api_name', 'status'])
PROCESSED_VIDEOS = Counter('youtube2sheets_processed_videos_total', 'Processed videos')

class MetricsCollector:
    """Collects and exposes application metrics."""
    
    def __init__(self, port=8001):
        self.port = port
        start_http_server(port)
    
    def record_request(self, method: str, endpoint: str, duration: float):
        """Record request metrics."""
        REQUEST_COUNT.labels(method=method, endpoint=endpoint).inc()
        REQUEST_DURATION.observe(duration)
    
    def record_api_call(self, api_name: str, status: str):
        """Record API call metrics."""
        API_CALLS.labels(api_name=api_name, status=status).inc()
    
    def record_processed_videos(self, count: int):
        """Record processed videos count."""
        PROCESSED_VIDEOS.inc(count)
```

#### Logging Configuration
```python
# logging/config.py
import logging
import logging.handlers
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry)

def setup_logging():
    """Setup structured logging configuration."""
    # Create logger
    logger = logging.getLogger('youtube2sheets')
    logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        'logs/youtube2sheets.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)
    
    return logger
```

#### Alerting Configuration
```yaml
# monitoring/alerts.yml
groups:
  - name: youtube2sheets
    rules:
      - alert: HighErrorRate
        expr: rate(youtube2sheets_requests_total{status="error"}[5m]) > 0.1
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors per second"
      
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(youtube2sheets_request_duration_seconds_bucket[5m])) > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time detected"
          description: "95th percentile response time is {{ $value }} seconds"
      
      - alert: APIQuotaExceeded
        expr: youtube2sheets_api_calls_total{api_name="youtube", status="quota_exceeded"} > 0
        for: 0m
        labels:
          severity: critical
        annotations:
          summary: "YouTube API quota exceeded"
          description: "YouTube API quota has been exceeded"
      
      - alert: ServiceDown
        expr: up{job="youtube2sheets"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "YouTube2Sheets service is down"
          description: "Service has been down for more than 1 minute"
```

### Security and Compliance

#### Security Scanning
```yaml
# .github/workflows/security.yml
name: Security Scan

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
      
      - name: Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
      
      - name: Run Bandit security linter
        run: |
          pip install bandit
          bandit -r youtube_to_sheets/ -f json -o bandit-report.json
      
      - name: Run Safety check
        run: |
          pip install safety
          safety check --json --output safety-report.json
```

#### Infrastructure Security
```yaml
# security/security-groups.tf
resource "aws_security_group" "youtube2sheets_sg" {
  name_prefix = "youtube2sheets-"
  vpc_id      = aws_vpc.youtube2sheets_vpc.id

  # Allow HTTP traffic
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow HTTPS traffic
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow SSH from bastion host
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [aws_subnet.bastion_subnet.cidr_block]
  }

  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "youtube2sheets-security-group"
  }
}
```

### Environment Management

#### Environment Configuration
```python
# config/environments.py
import os
from enum import Enum

class Environment(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class Config:
    """Base configuration class."""
    
    # Common settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DEBUG = False
    TESTING = False
    
    # Database settings
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # API settings
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
    GOOGLE_SHEETS_CREDENTIALS = os.getenv('GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON')
    
    # Logging settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/youtube2sheets.log')
    
    # Performance settings
    MAX_WORKERS = int(os.getenv('MAX_WORKERS', '4'))
    CACHE_SIZE = int(os.getenv('CACHE_SIZE', '1000'))
    RATE_LIMIT_DELAY = float(os.getenv('RATE_LIMIT_DELAY', '0.1'))

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class StagingConfig(Config):
    """Staging configuration."""
    DEBUG = False
    LOG_LEVEL = 'INFO'

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    LOG_LEVEL = 'WARNING'

def get_config():
    """Get configuration based on environment."""
    env = os.getenv('ENVIRONMENT', 'development')
    
    if env == 'development':
        return DevelopmentConfig()
    elif env == 'staging':
        return StagingConfig()
    elif env == 'production':
        return ProductionConfig()
    else:
        raise ValueError(f"Unknown environment: {env}")
```

### Backup and Recovery

#### Backup Strategy
```python
# backup/backup_manager.py
import boto3
import os
from datetime import datetime, timedelta
from typing import List

class BackupManager:
    """Manages backup and recovery operations."""
    
    def __init__(self, s3_bucket: str, region: str = 'us-west-2'):
        self.s3_bucket = s3_bucket
        self.s3_client = boto3.client('s3', region_name=region)
    
    def backup_database(self, db_name: str) -> str:
        """Create database backup."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"backups/{db_name}_{timestamp}.sql"
        
        # Create database dump
        os.system(f"pg_dump {db_name} > {backup_filename}")
        
        # Upload to S3
        self.s3_client.upload_file(backup_filename, self.s3_bucket, backup_filename)
        
        # Clean up local file
        os.remove(backup_filename)
        
        return backup_filename
    
    def backup_logs(self) -> str:
        """Backup application logs."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_filename = f"logs/youtube2sheets_{timestamp}.tar.gz"
        
        # Create log archive
        os.system(f"tar -czf {log_filename} logs/")
        
        # Upload to S3
        self.s3_client.upload_file(log_filename, self.s3_bucket, log_filename)
        
        # Clean up local file
        os.remove(log_filename)
        
        return log_filename
    
    def cleanup_old_backups(self, days_to_keep: int = 30):
        """Clean up old backups."""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        # List all backups
        response = self.s3_client.list_objects_v2(Bucket=self.s3_bucket, Prefix='backups/')
        
        for obj in response.get('Contents', []):
            if obj['LastModified'].replace(tzinfo=None) < cutoff_date:
                self.s3_client.delete_object(Bucket=self.s3_bucket, Key=obj['Key'])
```

### Performance Optimization

#### Caching Strategy
```python
# caching/redis_cache.py
import redis
import json
import pickle
from typing import Any, Optional
from datetime import timedelta

class RedisCache:
    """Redis-based caching implementation."""
    
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        self.redis_client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL."""
        try:
            serialized_value = json.dumps(value)
            return self.redis_client.setex(key, ttl, serialized_value)
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache clear pattern error: {e}")
            return 0
```

### Success Metrics

#### Deployment Metrics
- **Deployment Frequency**: Daily deployments
- **Lead Time**: < 1 hour from commit to production
- **Mean Time to Recovery**: < 30 minutes
- **Change Failure Rate**: < 5%

#### Infrastructure Metrics
- **Uptime**: 99.9% availability
- **Response Time**: < 2 seconds average
- **Error Rate**: < 0.1% error rate
- **Resource Utilization**: < 80% CPU/Memory

### Collaboration Patterns

#### With Lead Engineer
- Coordinate deployment processes
- Ensure infrastructure supports development needs
- Implement monitoring and alerting
- Optimize development workflows

#### With Security Engineer
- Implement security controls in infrastructure
- Ensure secure deployment processes
- Coordinate security monitoring
- Validate compliance requirements

#### With Project Manager
- Provide infrastructure estimates
- Coordinate deployment timelines
- Report on infrastructure status
- Identify infrastructure risks and mitigation
