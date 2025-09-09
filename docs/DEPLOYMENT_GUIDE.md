# Deployment Guide - Yahoo Fantasy Baseball Analyzer

Complete guide for deploying the Yahoo Fantasy Baseball Analyzer to Streamlit Cloud and other platforms.

## 📚 Table of Contents

1. [Streamlit Cloud Deployment](#streamlit-cloud-deployment)
2. [Pre-deployment Checklist](#pre-deployment-checklist)
3. [Environment Configuration](#environment-configuration)
4. [Security Best Practices](#security-best-practices)
5. [Monitoring and Maintenance](#monitoring-and-maintenance)
6. [Troubleshooting Deployment Issues](#troubleshooting-deployment-issues)
7. [Alternative Deployment Options](#alternative-deployment-options)

## 🚀 Streamlit Cloud Deployment

### Prerequisites

- GitHub account with repository access
- Yahoo Developer App credentials
- Streamlit Cloud account (free at [share.streamlit.io](https://share.streamlit.io))

### Step 1: Repository Preparation

#### 1.1 Verify Repository Structure
Ensure your repository has the correct structure:

```
yahoo-fantasy-baseball-streamlit/
├── app.py                    # ✅ Main app file at root level
├── requirements.txt          # ✅ Dependencies list
├── .streamlit/
│   ├── config.toml          # ✅ Streamlit configuration
│   └── secrets.toml.example # ✅ Secrets template
├── src/                     # ✅ Source code
└── docs/                    # ✅ Documentation
```

#### 1.2 Check Requirements File
Verify `requirements.txt` contains all dependencies:

```txt
streamlit>=1.28.0
pandas>=2.0.0
requests>=2.31.0
yahoo-fantasy-api>=2.2.0
yahoo-oauth>=1.0.0
python-dateutil>=2.8.0
pydantic>=2.0.0
typing-extensions>=4.0.0
```

#### 1.3 Validate Main App File
Ensure `app.py` is at the root level and contains:

```python
# app.py
import streamlit as st
from src.core.config import get_config

def main() -> None:
    """Main application entry point."""
    # Application code here
    pass

if __name__ == "__main__":
    main()
```

### Step 2: Streamlit Cloud Setup

#### 2.1 Create Streamlit Cloud Account
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "Sign up" or "Continue with GitHub"
3. Authorize Streamlit to access your GitHub repositories

#### 2.2 Deploy Application
1. **Click "New app"**
2. **Select repository**: Choose your GitHub repository
3. **Configure deployment settings**:
   - **Repository**: `yourusername/yahoo-fantasy-baseball-streamlit`
   - **Branch**: `main` (or your default branch)
   - **Main file path**: `app.py`
   - **App URL**: Choose a custom URL (optional)

#### 2.3 Advanced Settings (Optional)
- **Python version**: 3.8, 3.9, 3.10, or 3.11
- **Custom requirements**: Leave blank (uses requirements.txt)

### Step 3: Configure Secrets

#### 3.1 Access Secrets Management
1. After deployment starts, click on your app
2. Go to "Settings" → "Secrets"
3. You'll see a text editor for secrets configuration

#### 3.2 Add Production Secrets
Copy and paste your secrets configuration:

```toml
[yahoo_oauth]
client_id = "your_production_client_id"
client_secret = "your_production_client_secret"
access_token = "your_production_access_token"
refresh_token = "your_production_refresh_token"

[app_config]
default_league_id = "458.l.135626"
default_team_key = "458.l.135626.t.6"
cache_ttl_seconds = 3600
max_retries = 3
request_timeout = 10
analysis_days_ahead = 10
ownership_threshold = 50.0

[logging]
level = "INFO"
format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

#### 3.3 Save and Deploy
1. Click "Save"
2. Streamlit Cloud will automatically redeploy with new secrets
3. Monitor deployment logs for any issues

### Step 4: Verify Deployment

#### 4.1 Check Application Status
- **Green dot**: Application is running successfully
- **Red dot**: Deployment failed (check logs)
- **Yellow dot**: Application is starting up

#### 4.2 Test Core Functionality
1. **Access the application** via the provided URL
2. **Test configuration**: Enter a valid team key
3. **Verify UI**: Check that all components load correctly
4. **Test analysis**: Run a sample analysis (if you have valid credentials)

#### 4.3 Monitor Performance
- Check application response times
- Verify memory usage is within limits
- Monitor for any error messages

## ✅ Pre-deployment Checklist

### Code Quality
- [ ] All tests pass locally (`pytest`)
- [ ] Code follows style guidelines (`black`, `flake8`)
- [ ] Type checking passes (`mypy`)
- [ ] No hardcoded secrets in code
- [ ] Error handling implemented for all API calls

### Configuration
- [ ] `requirements.txt` is complete and up-to-date
- [ ] `app.py` is at repository root
- [ ] `.streamlit/config.toml` configured for production
- [ ] Secrets template (`.streamlit/secrets.toml.example`) is provided
- [ ] No actual secrets committed to repository

### Documentation
- [ ] README.md is comprehensive and up-to-date
- [ ] User guide explains how to find team keys
- [ ] Deployment instructions are clear
- [ ] Troubleshooting section covers common issues

### Security
- [ ] Yahoo OAuth credentials are production-ready
- [ ] API rate limiting is implemented
- [ ] Input validation is comprehensive
- [ ] Error messages don't expose sensitive information

## 🔧 Environment Configuration

### Streamlit Configuration

Create or update `.streamlit/config.toml`:

```toml
[global]
# Production settings
developmentMode = false
logLevel = "info"

[server]
# Server configuration
port = 8501
enableCORS = false
enableXsrfProtection = true
maxUploadSize = 200

[browser]
# Browser settings
gatherUsageStats = false
serverAddress = "0.0.0.0"

[theme]
# UI theme
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

### Environment-Specific Settings

#### Production Configuration
```python
# src/core/config.py
def get_production_config():
    """Get production-specific configuration."""
    return {
        'cache_ttl_seconds': 3600,  # 1 hour cache
        'max_retries': 3,
        'request_timeout': 10,
        'log_level': 'INFO',
        'enable_debug': False
    }
```

#### Development Configuration
```python
def get_development_config():
    """Get development-specific configuration."""
    return {
        'cache_ttl_seconds': 300,   # 5 minute cache
        'max_retries': 1,
        'request_timeout': 5,
        'log_level': 'DEBUG',
        'enable_debug': True
    }
```

## 🔒 Security Best Practices

### Secrets Management

#### 1. Never Commit Secrets
```bash
# Add to .gitignore
.streamlit/secrets.toml
*.env
.env.*
config/secrets.json
```

#### 2. Use Environment-Specific Secrets
- **Development**: Local `.streamlit/secrets.toml`
- **Production**: Streamlit Cloud secrets management
- **Testing**: Mock credentials or test environment

#### 3. Rotate Credentials Regularly
- Update Yahoo OAuth tokens quarterly
- Monitor for any unauthorized access
- Use separate credentials for different environments

### API Security

#### 1. Rate Limiting
```python
# src/api/base_client.py
class BaseAPIClient:
    def __init__(self):
        self.rate_limiter = RateLimiter(
            max_calls=100,
            time_window=60  # 100 calls per minute
        )
    
    def _make_request(self, *args, **kwargs):
        self.rate_limiter.wait_if_needed()
        # Make request
```

#### 2. Input Validation
```python
# src/core/validation.py
def validate_team_key(team_key: str) -> bool:
    """Validate team key format and prevent injection."""
    pattern = r'^\d+\.l\.\d+\.t\.\d+$'
    return bool(re.match(pattern, team_key.strip()))
```

#### 3. Error Handling
```python
# Don't expose internal details
try:
    result = api_call()
except APIError as e:
    logger.error(f"API error: {e}")
    st.error("Unable to fetch data. Please try again later.")
```

### Data Privacy

#### 1. No Data Persistence
- Don't store user data permanently
- Clear session data appropriately
- Use in-memory caching only

#### 2. Minimal Data Collection
- Only request necessary permissions
- Don't log sensitive information
- Respect user privacy preferences

## 📊 Monitoring and Maintenance

### Application Monitoring

#### 1. Health Checks
```python
# src/utils/health_check.py
def check_application_health():
    """Perform basic health checks."""
    checks = {
        'config_loaded': check_config(),
        'apis_accessible': check_api_connectivity(),
        'cache_working': check_cache_service()
    }
    return all(checks.values()), checks
```

#### 2. Performance Monitoring
- Monitor response times
- Track memory usage
- Watch for API rate limits
- Monitor error rates

#### 3. User Analytics
```python
# src/utils/analytics.py
def log_user_action(action: str, metadata: dict = None):
    """Log user actions for analytics."""
    if not st.secrets.get('enable_analytics', False):
        return
    
    # Log anonymized usage data
    logger.info(f"User action: {action}", extra=metadata)
```

### Maintenance Tasks

#### Weekly Tasks
- [ ] Check application logs for errors
- [ ] Verify API connectivity
- [ ] Monitor performance metrics
- [ ] Review user feedback

#### Monthly Tasks
- [ ] Update dependencies if needed
- [ ] Review and rotate secrets
- [ ] Analyze usage patterns
- [ ] Update documentation

#### Quarterly Tasks
- [ ] Security audit
- [ ] Performance optimization review
- [ ] User experience assessment
- [ ] Backup and disaster recovery testing

### Automated Monitoring

#### GitHub Actions Workflow
```yaml
# .github/workflows/health-check.yml
name: Application Health Check

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours

jobs:
  health-check:
    runs-on: ubuntu-latest
    steps:
      - name: Check Application
        run: |
          curl -f ${{ secrets.APP_URL }}/health || exit 1
```

## 🔧 Troubleshooting Deployment Issues

### Common Deployment Problems

#### 1. Import Errors
**Problem**: `ModuleNotFoundError` during deployment

**Solutions**:
```bash
# Check requirements.txt completeness
pip freeze > requirements-check.txt
diff requirements.txt requirements-check.txt

# Verify Python path
# Add to app.py if needed:
import sys
import os
sys.path.append(os.path.dirname(__file__))
```

#### 2. Secrets Not Loading
**Problem**: Configuration errors related to missing secrets

**Solutions**:
- Verify secrets format in Streamlit Cloud
- Check for typos in secret keys
- Ensure all required secrets are present
- Test with minimal secrets configuration

#### 3. Memory Limits
**Problem**: Application crashes due to memory usage

**Solutions**:
```python
# Optimize memory usage
import gc

def optimize_memory():
    """Optimize memory usage."""
    # Clear unused variables
    gc.collect()
    
    # Use generators instead of lists
    # Implement lazy loading
    # Cache only essential data
```

#### 4. API Rate Limiting
**Problem**: Yahoo API rate limit exceeded

**Solutions**:
```python
# Implement exponential backoff
import time
import random

def retry_with_backoff(func, max_retries=3):
    """Retry function with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError:
            if attempt == max_retries - 1:
                raise
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(wait_time)
```

### Debugging Tools

#### 1. Enable Debug Mode
```python
# In secrets.toml
[app_config]
debug_mode = true
log_level = "DEBUG"
```

#### 2. Add Logging
```python
import logging

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.debug("Debug information here")
```

#### 3. Error Tracking
```python
# Add error context
try:
    risky_operation()
except Exception as e:
    logger.error(f"Error in {operation_name}: {e}", exc_info=True)
    st.error(f"Operation failed: {operation_name}")
```

## 🌐 Alternative Deployment Options

### Heroku Deployment

#### 1. Prepare for Heroku
```bash
# Create Procfile
echo "web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0" > Procfile

# Create runtime.txt
echo "python-3.9.16" > runtime.txt
```

#### 2. Deploy to Heroku
```bash
heroku create your-app-name
heroku config:set YAHOO_CLIENT_ID=your_client_id
heroku config:set YAHOO_CLIENT_SECRET=your_client_secret
git push heroku main
```

### Docker Deployment

#### 1. Create Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
```

#### 2. Build and Run
```bash
docker build -t yahoo-fantasy-analyzer .
docker run -p 8501:8501 yahoo-fantasy-analyzer
```

### AWS EC2 Deployment

#### 1. Setup EC2 Instance
```bash
# Install dependencies
sudo apt update
sudo apt install python3-pip nginx

# Clone repository
git clone your-repository-url
cd yahoo-fantasy-baseball-streamlit

# Install requirements
pip3 install -r requirements.txt
```

#### 2. Configure Nginx
```nginx
# /etc/nginx/sites-available/streamlit
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📞 Support and Resources

### Streamlit Cloud Resources
- [Streamlit Cloud Documentation](https://docs.streamlit.io/streamlit-cloud)
- [Community Forum](https://discuss.streamlit.io/)
- [GitHub Issues](https://github.com/streamlit/streamlit/issues)

### Yahoo Fantasy API Resources
- [Yahoo Developer Documentation](https://developer.yahoo.com/fantasysports/)
- [OAuth Guide](https://developer.yahoo.com/oauth2/guide/)
- [API Reference](https://developer.yahoo.com/fantasysports/guide/)

### Monitoring Tools
- [Streamlit Cloud Analytics](https://share.streamlit.io/)
- [GitHub Actions](https://github.com/features/actions)
- [Uptime Robot](https://uptimerobot.com/) (external monitoring)

---

**Successful deployment! Your Yahoo Fantasy Baseball Analyzer is now live! 🚀⚾**