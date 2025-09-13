# Deployment Security Guide

## 🔒 Security Analysis Summary

### Current Security Status
✅ **Good Practices Found:**
- OAuth credentials properly excluded from git (`.gitignore`)
- No hardcoded secrets in source code
- Credentials loaded from Streamlit secrets
- Session-based caching (user data isolation)

⚠️ **Critical Security Issues for Public Deployment:**

## 🚨 CRITICAL ISSUES TO ADDRESS

### 1. **Shared OAuth Credentials Problem**
**Current State:** The app uses a single set of OAuth credentials for all users.

**Risk:**
- All users would share the same Yahoo OAuth tokens
- Users could potentially access each other's Yahoo Fantasy data
- Single point of failure if tokens are compromised

**Solution Required:**
```python
# OPTION 1: Each user brings their own OAuth credentials
# Modify sidebar_enhanced.py to accept OAuth input from users

# OPTION 2: OAuth flow implementation
# Implement proper OAuth2 flow where each user authorizes individually
```

### 2. **Missing Rate Limiting**
**Current State:** No rate limiting on API calls.

**Risk:**
- Single user could exhaust API limits
- DoS vulnerability

**Solution:**
```python
# Add to cache_service.py or create rate_limiter.py
from datetime import datetime, timedelta
import streamlit as st

class RateLimiter:
    def __init__(self, max_requests=100, time_window=3600):
        if 'rate_limits' not in st.session_state:
            st.session_state.rate_limits = {}

    def check_rate_limit(self, user_id):
        # Implementation here
        pass
```

### 3. **Session State Data Isolation**
**Current State:** Uses `st.session_state` which is properly isolated per user session.

**Status:** ✅ SECURE - Streamlit handles session isolation correctly.

## 📋 Pre-Deployment Checklist

### Required Changes for Public Deployment

#### 1. **Implement User-Specific OAuth**
```python
# In src/ui/components/sidebar_enhanced.py
def render_oauth_input():
    """Allow users to input their own OAuth credentials."""
    st.sidebar.markdown("### Yahoo OAuth Credentials")

    with st.sidebar.expander("OAuth Setup", expanded=False):
        client_id = st.text_input("Client ID", type="password", key="user_client_id")
        client_secret = st.text_input("Client Secret", type="password", key="user_client_secret")
        access_token = st.text_input("Access Token", type="password", key="user_access_token")
        refresh_token = st.text_input("Refresh Token", type="password", key="user_refresh_token")

        if st.button("Save Credentials"):
            # Store in session state only (never persist)
            st.session_state['user_oauth'] = {
                'client_id': client_id,
                'client_secret': client_secret,
                'access_token': access_token,
                'refresh_token': refresh_token
            }
```

#### 2. **Add Rate Limiting**
Create `src/services/rate_limiter.py`:
```python
import time
from typing import Dict, Tuple
import streamlit as st

class RateLimiter:
    """Rate limiting service for API calls."""

    def __init__(self):
        if 'rate_limit_data' not in st.session_state:
            st.session_state.rate_limit_data = {}

    def check_limit(self, key: str, max_calls: int = 100, window_seconds: int = 3600) -> Tuple[bool, int]:
        """
        Check if rate limit exceeded.
        Returns (allowed, remaining_calls)
        """
        current_time = time.time()

        if key not in st.session_state.rate_limit_data:
            st.session_state.rate_limit_data[key] = []

        # Clean old entries
        st.session_state.rate_limit_data[key] = [
            t for t in st.session_state.rate_limit_data[key]
            if current_time - t < window_seconds
        ]

        calls_made = len(st.session_state.rate_limit_data[key])

        if calls_made >= max_calls:
            return False, 0

        st.session_state.rate_limit_data[key].append(current_time)
        return True, max_calls - calls_made - 1
```

#### 3. **Add Input Validation**
Create `src/utils/validators.py`:
```python
import re
from typing import Optional

def sanitize_league_id(league_id: str) -> Optional[str]:
    """Sanitize and validate league ID input."""
    # Remove any potentially harmful characters
    cleaned = re.sub(r'[^0-9a-zA-Z\.\-]', '', league_id)

    # Validate format
    if re.match(r'^\d+\.l\.\d+$', cleaned):
        return cleaned
    return None

def sanitize_team_key(team_key: str) -> Optional[str]:
    """Sanitize and validate team key input."""
    cleaned = re.sub(r'[^0-9a-zA-Z\.\-]', '', team_key)

    if re.match(r'^\d+\.l\.\d+\.t\.\d+$', cleaned):
        return cleaned
    return None
```

#### 4. **Environment Variables Setup**
Create `.env.example`:
```bash
# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_ENABLE_CORS=false
STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=true

# App Configuration
MAX_REQUESTS_PER_HOUR=100
CACHE_TTL_SECONDS=3600
ENABLE_DEBUG_MODE=false
```

#### 5. **Update Requirements**
Add security-related packages to `requirements.txt`:
```txt
python-dotenv>=1.0.0
cryptography>=41.0.0  # For encrypting session data if needed
```

## 🚀 Deployment Steps

### For Streamlit Cloud Deployment

1. **Fork and prepare repository:**
   ```bash
   # Remove any test data or personal information
   git rm -r --cached .streamlit/secrets.toml
   git rm -r --cached yahoo_oauth.json
   ```

2. **Update app for user OAuth:**
   - Modify `src/api/custom_yahoo_oauth.py` to accept user credentials
   - Update `sidebar_enhanced.py` to include OAuth input UI
   - Remove default OAuth loading from `config.py`

3. **Add user instructions:**
   Create `USER_SETUP.md`:
   ```markdown
   # Setup Instructions

   1. Create Yahoo App at https://developer.yahoo.com
   2. Get your OAuth credentials
   3. Enter credentials in the sidebar
   4. Your credentials are only stored for your session
   ```

4. **Deploy to Streamlit Cloud:**
   - Don't add any secrets to Streamlit Cloud
   - Let users provide their own credentials

### Security Headers (for custom deployment)
If deploying on your own server, add these headers:
```python
# In app.py or server config
headers = {
    'X-Frame-Options': 'DENY',
    'X-Content-Type-Options': 'nosniff',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Content-Security-Policy': "default-src 'self'"
}
```

## 🔐 Data Privacy Considerations

1. **User Data:**
   - Never log OAuth credentials
   - Clear session data on logout
   - Don't persist user data between sessions

2. **API Keys:**
   - Each user must provide their own
   - Never share keys between users
   - Implement key rotation reminders

3. **League Data:**
   - Only access leagues user has permission for
   - Don't cache data across users
   - Clear all data on session end

## ⚠️ Current Vulnerabilities Summary

| Issue | Severity | Status | Required Action |
|-------|----------|--------|-----------------|
| Shared OAuth Credentials | CRITICAL | ❌ | Implement user-specific OAuth |
| No Rate Limiting | HIGH | ❌ | Add rate limiter |
| No Input Sanitization | MEDIUM | ❌ | Add validators |
| Session Data Isolation | LOW | ✅ | Already handled by Streamlit |
| HTTPS | LOW | ✅ | Handled by Streamlit Cloud |

## 📝 Post-Deployment Monitoring

1. **Add logging for:**
   - Failed OAuth attempts
   - Rate limit hits
   - API errors
   - Unusual access patterns

2. **Monitor:**
   - API quota usage
   - Error rates
   - User session duration
   - Memory usage

## 🚦 Go/No-Go Decision

**Current State: NOT READY for public deployment**

**Required before deployment:**
1. ✅ Remove all default OAuth credentials
2. ✅ Implement user-specific OAuth input
3. ✅ Add rate limiting
4. ✅ Add input validation
5. ✅ Create user setup documentation

**Estimated effort: 4-6 hours of development**

## Alternative: Limited Private Deployment

If you want to deploy for a small group NOW:

1. **Create separate Streamlit apps** for each user
2. **Use Streamlit's private sharing** (requires Pro account)
3. **Give each user their own secrets.toml**
4. **Monitor usage carefully**

This avoids the OAuth sharing issue but doesn't scale.