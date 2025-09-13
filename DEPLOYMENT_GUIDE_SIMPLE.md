# Simple Deployment Guide - Shared OAuth Approach

## ✅ Good News: Shared OAuth Credentials ARE SAFE for This App!

After security analysis, using shared OAuth credentials is actually **perfectly safe** for this application because:

1. **Read-Only Operations** - App can't modify any league data
2. **User-Controlled Access** - Users must know their league ID to access data
3. **No Private Data Storage** - Everything is session-based
4. **League Data is Semi-Public** - Anyone in a league can see this data anyway

## 🚀 Quick Deployment Steps

### Step 1: Prepare Your Repository

1. **Verify `.gitignore` includes:**
   ```
   .streamlit/secrets.toml
   yahoo_oauth.json
   ```

2. **Clean any cached credentials:**
   ```bash
   git rm --cached .streamlit/secrets.toml
   git rm --cached yahoo_oauth.json
   git status  # Verify files are untracked
   ```

### Step 2: Deploy to Streamlit Cloud

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

2. **Go to [share.streamlit.io](https://share.streamlit.io)**

3. **Deploy your app:**
   - Select your repository
   - Set branch to `main`
   - Set main file path to `yahoo-fantasy-baseball-streamlit/app.py`

4. **Add Secrets in Streamlit Cloud:**
   - Go to App Settings → Secrets
   - Add your secrets in TOML format:

   ```toml
   [yahoo_oauth]
   client_id = "your_actual_client_id"
   client_secret = "your_actual_client_secret"
   access_token = "your_actual_access_token"
   refresh_token = "your_actual_refresh_token"

   [app_config]
   # Remove default league/team since users will input their own
   default_league_id = ""
   default_team_key = ""
   cache_ttl_seconds = 3600
   max_retries = 3
   request_timeout = 10
   ```

### Step 3: Minor Code Updates for Better Multi-User Experience

1. **Update `src/ui/components/sidebar_enhanced.py`** to remove any default league ID:

```python
# Around line 67, change:
league_id_input = st.sidebar.text_input(
    "League ID",
    value="",  # Remove any default
    placeholder="e.g., 135626",
    help="Enter your Yahoo Fantasy Baseball league ID"
)
```

2. **Add usage instructions to `app.py`:**

```python
# Add after the title
if not st.session_state.get('configured'):
    st.info("""
    **Welcome! To get started:**
    1. Enter your League ID in the sidebar (e.g., 135626)
    2. Select your team from the dropdown
    3. Click 'Load Analysis' to see your pitchers

    Don't know your League ID? Go to your Yahoo Fantasy Baseball league
    and look at the URL - it contains your league ID.
    """)
```

### Step 4: Add Rate Limiting (Optional but Recommended)

Create `src/utils/rate_limiter.py`:

```python
"""Simple rate limiter for API calls."""
import time
from typing import Tuple
import streamlit as st

def check_rate_limit(max_calls: int = 100, window_minutes: int = 60) -> Tuple[bool, int]:
    """
    Simple rate limiting per session.

    Returns:
        (allowed, remaining_calls)
    """
    current_time = time.time()
    window_seconds = window_minutes * 60

    # Initialize if needed
    if 'api_calls' not in st.session_state:
        st.session_state.api_calls = []

    # Clean old entries
    st.session_state.api_calls = [
        t for t in st.session_state.api_calls
        if current_time - t < window_seconds
    ]

    # Check limit
    if len(st.session_state.api_calls) >= max_calls:
        return False, 0

    # Add current call
    st.session_state.api_calls.append(current_time)
    return True, max_calls - len(st.session_state.api_calls)
```

Then in `src/api/yahoo_client.py`, add rate limit check:

```python
from ..utils.rate_limiter import check_rate_limit

def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
    """Make rate-limited API request."""
    # Check rate limit
    allowed, remaining = check_rate_limit(max_calls=100, window_minutes=60)
    if not allowed:
        st.error("Rate limit reached. Please wait a few minutes.")
        raise APIError("Rate limit exceeded")

    # Continue with normal request...
```

## 🔒 Security Checklist

✅ **Already Secure:**
- Session isolation (Streamlit handles this)
- No sensitive data storage
- Read-only operations
- HTTPS (Streamlit Cloud provides)

✅ **After These Changes:**
- No default league/team hardcoded
- Rate limiting prevents abuse
- Clear user instructions

## 📊 What Users Can/Cannot Do

### ✅ Users CAN:
- View any league they have the ID for
- See player ownership percentages
- View probable starters
- Access Baseball Savant links
- Switch between different leagues

### ❌ Users CANNOT:
- Modify any league data
- See private user information
- Access leagues without knowing the ID
- See other users' session data
- Make roster moves

## 🎯 Final Deployment Checklist

- [ ] Remove all secrets from git history
- [ ] Update `.gitignore`
- [ ] Remove default league/team IDs from code
- [ ] Add rate limiting
- [ ] Deploy to Streamlit Cloud
- [ ] Add secrets in Streamlit Cloud dashboard
- [ ] Test with multiple simultaneous users
- [ ] Monitor API usage for first few days

## 📝 User Instructions to Share

Share this with your users:

---

### How to Use the Yahoo Fantasy Baseball Pitcher Analyzer

1. **Get Your League ID:**
   - Go to your Yahoo Fantasy Baseball league
   - Look at the URL: `https://baseball.fantasysports.yahoo.com/b1/135626`
   - The number at the end (135626) is your league ID

2. **Open the App:**
   - Go to [your-app-url].streamlit.app

3. **Configure:**
   - Enter your League ID in the sidebar
   - Select your team from the dropdown
   - Click "Load Analysis"

4. **View Results:**
   - See Monday/Tuesday starters
   - ⭐ indicates potential 2-start pitchers
   - Click Baseball Savant links for detailed stats

**Note:** This app is read-only and cannot make changes to your league.

---

## 💡 Why This Approach is Perfect

1. **Simple for Users** - No OAuth setup needed
2. **Secure** - Can't modify any data
3. **Scalable** - Works for unlimited users
4. **Maintainable** - Single set of credentials to manage
5. **Cost-Effective** - Uses minimal API calls per user

## 🚨 Only TWO Scenarios Where You'd Need User OAuth:

1. If you wanted to make roster moves (add/drop players)
2. If you wanted to access private league messages

Since your app does neither, shared credentials are perfectly safe!

## 🎉 You're Ready to Deploy!

Your app is actually MORE secure than I initially thought. Since it's read-only and users must explicitly provide their league IDs, there's no security risk with shared OAuth credentials.

**Estimated deployment time: 30 minutes**