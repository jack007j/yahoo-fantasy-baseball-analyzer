# Token Refresh Guide

## ⚠️ Yahoo OAuth Tokens Expire!

Yahoo OAuth tokens expire periodically and need to be refreshed. When you see this error:
```
"token_expired", realm="yahooapis.com"
```

## 🔄 How to Refresh Tokens

### Step 1: Generate New Tokens Locally
```bash
cd yahoo-fantasy-baseball-streamlit
python generate_oauth_tokens.py
```

Follow the prompts:
1. Enter your Client ID (same as before)
2. Enter your Client Secret (same as before)
3. Open the URL it provides in your browser
4. Authorize the app
5. Copy the verification code back to the terminal

### Step 2: Update Streamlit Cloud Secrets

1. Go to your app on [share.streamlit.io](https://share.streamlit.io)
2. Click Settings → Secrets
3. Update ONLY these two lines with the new values from Step 1:
   ```toml
   access_token = "NEW_ACCESS_TOKEN_HERE"
   refresh_token = "NEW_REFRESH_TOKEN_HERE"
   ```
4. Keep `client_id` and `client_secret` the same
5. Save

### Step 3: Restart App
The app will automatically restart with the new tokens.

## 📅 Token Lifespan

### Yahoo OAuth Token Expiration Times:
- **Access tokens**: Expire after **1 hour** of being generated
- **Refresh tokens**: Valid for **up to 6 months** (but can expire sooner with policy changes)
- **After refresh token expires**: Must re-authenticate completely with generate_oauth_tokens.py

### What This Means for Your App:
- **First hour**: Everything works perfectly
- **After 1 hour**: Access token expires, app tries to use refresh token
- **If refresh works**: New access token is generated automatically (but not saved to Streamlit secrets)
- **If refresh fails**: Need to manually generate new tokens

### Best Practice:
- **Generate fresh tokens** right before deploying
- **Regenerate monthly** to avoid refresh token expiration
- **Set a calendar reminder** to refresh tokens periodically

## 🤖 Automated Solution (Future Enhancement)

To avoid manual refreshing, we could:
1. Implement automatic token refresh using the refresh_token
2. Store tokens in a database that the app can update
3. Use a scheduled job to refresh tokens before they expire

## 🚨 Quick Fix for Now

Since manual entry is working, you can use the app even with expired tokens by:
1. Enter your League ID
2. Enter your Team Number manually (e.g., "6")
3. The app will still work for analysis!

The team dropdown is a convenience feature - the app works fine without it.