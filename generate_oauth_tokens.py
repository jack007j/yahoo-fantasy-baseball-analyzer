#!/usr/bin/env python3
"""
Yahoo OAuth Token Generator

This script helps you generate the Access Token and Refresh Token needed
for the Yahoo Fantasy Baseball application using your Client ID and Client Secret.

Run this script once to get your tokens, then add them to secrets.toml
"""

import os
import sys
from yahoo_oauth import OAuth2

def generate_tokens():
    """Generate Yahoo OAuth tokens interactively."""
    
    print("🔐 Yahoo OAuth Token Generator")
    print("=" * 50)
    print()
    
    # Get Client ID and Client Secret from user
    print("Please enter your Yahoo Developer App credentials:")
    print("(You can find these in your Yahoo Developer Console)")
    print()
    
    client_id = input("Enter your Client ID: ").strip()
    if not client_id:
        print("❌ Client ID is required!")
        return False
    
    client_secret = input("Enter your Client Secret: ").strip()
    if not client_secret:
        print("❌ Client Secret is required!")
        return False
    
    print()
    print("🔄 Starting OAuth flow...")
    print()
    
    try:
        # Create OAuth2 client
        # This will open a browser window for you to authorize the app
        oauth = OAuth2(
            consumer_key=client_id,
            consumer_secret=client_secret,
            redirect_uri='oob'  # Out-of-band for desktop apps
        )
        
        print("✅ OAuth flow completed successfully!")
        print()
        print("🎉 Your tokens have been generated:")
        print("=" * 50)
        print(f"Client ID: {client_id}")
        print(f"Client Secret: {client_secret}")
        print(f"Access Token: {oauth.access_token}")
        print(f"Refresh Token: {oauth.refresh_token}")
        print("=" * 50)
        print()
        
        # Update secrets.toml automatically
        update_secrets_file(client_id, client_secret, oauth.access_token, oauth.refresh_token)
        
        return True
        
    except Exception as e:
        print(f"❌ Error during OAuth flow: {str(e)}")
        print()
        print("💡 Troubleshooting tips:")
        print("- Make sure your Client ID and Client Secret are correct")
        print("- Ensure your Yahoo Developer App has Fantasy Sports API access")
        print("- Check that your redirect URI is set to 'oob' in Yahoo Developer Console")
        return False

def update_secrets_file(client_id, client_secret, access_token, refresh_token):
    """Update the secrets.toml file with the generated tokens."""
    
    secrets_path = ".streamlit/secrets.toml"
    
    try:
        # Read the current secrets file
        with open(secrets_path, 'r') as f:
            content = f.read()
        
        # Replace placeholder values
        content = content.replace('REPLACE_WITH_YOUR_CLIENT_ID', client_id)
        content = content.replace('REPLACE_WITH_YOUR_CLIENT_SECRET', client_secret)
        content = content.replace('REPLACE_WITH_YOUR_ACCESS_TOKEN', access_token)
        content = content.replace('REPLACE_WITH_YOUR_REFRESH_TOKEN', refresh_token)
        
        # Write back to file
        with open(secrets_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Updated {secrets_path} with your OAuth credentials!")
        print("🚀 You can now run the Streamlit app successfully!")
        
    except Exception as e:
        print(f"⚠️  Could not automatically update secrets.toml: {str(e)}")
        print()
        print("📝 Please manually update .streamlit/secrets.toml with these values:")
        print(f"client_id = \"{client_id}\"")
        print(f"client_secret = \"{client_secret}\"")
        print(f"access_token = \"{access_token}\"")
        print(f"refresh_token = \"{refresh_token}\"")

def main():
    """Main function."""
    
    # Check if we're in the right directory
    if not os.path.exists('.streamlit/secrets.toml'):
        print("❌ Error: .streamlit/secrets.toml not found!")
        print("Please run this script from the yahoo-fantasy-baseball-streamlit directory")
        return
    
    print("This script will help you generate Yahoo OAuth tokens.")
    print("It will open a browser window for you to authorize the app.")
    print()
    
    proceed = input("Ready to proceed? (y/n): ").strip().lower()
    if proceed not in ['y', 'yes']:
        print("Cancelled.")
        return
    
    print()
    success = generate_tokens()
    
    if success:
        print()
        print("🎉 Setup complete! Your Yahoo Fantasy Baseball app is ready to use.")
        print("You can now restart the Streamlit app and it should work without OAuth errors.")
    else:
        print()
        print("❌ Setup failed. Please check the error messages above and try again.")

if __name__ == "__main__":
    main()