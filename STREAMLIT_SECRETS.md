# Streamlit Secrets Configuration

For the Yahoo Fantasy Baseball Analyzer to work on Streamlit Cloud, you need to configure your OAuth credentials in Streamlit Secrets.

## Required Secrets

Add the following to your Streamlit app's secrets (Settings → Secrets):

```toml
[yahoo_oauth]
client_id = "your_yahoo_client_id"
client_secret = "your_yahoo_client_secret"
refresh_token = "your_refresh_token"
# The access_token is optional - it will be expired anyway and refreshed automatically
access_token = "optional_expired_token"
```

## Important Notes

1. **Access Token**: The access token in secrets will always be expired since tokens only last 1 hour. The app automatically refreshes it using the refresh token.

2. **Refresh Token**: This is the critical piece - it allows the app to get new access tokens. Make sure this is valid.

3. **Getting Tokens**: You need to run the OAuth flow locally once to get these tokens:
   - Run the app locally with `yahoo_oauth.json`
   - Complete the OAuth flow
   - Copy the refresh_token from the `yahoo_oauth.json` file
   - Add it to Streamlit secrets

4. **Token Sharing**: Be aware that using the same token across multiple users/IPs may cause Yahoo to reject requests. This setup is best for personal use or small groups.

## Troubleshooting

If you see "Please provide valid credentials" errors:

1. Check that your refresh_token in secrets is valid
2. Try the "Refresh OAuth Token" button in the app's sidebar
3. You may need to re-authenticate locally and update the refresh_token in secrets

## Security Considerations

- Don't share your client_secret or refresh_token publicly
- Consider that anyone with access to your deployed app can access your Yahoo Fantasy leagues
- For production multi-user apps, implement proper per-user OAuth flow