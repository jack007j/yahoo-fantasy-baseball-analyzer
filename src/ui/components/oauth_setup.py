"""
OAuth setup component for user-specific credentials.

This component allows each user to provide their own Yahoo OAuth credentials
for secure multi-user deployment.
"""

import streamlit as st
from typing import Dict, Optional
import json
import base64


def render_oauth_setup() -> Optional[Dict[str, str]]:
    """
    Render OAuth setup interface and return credentials if available.

    Returns:
        Dictionary with OAuth credentials or None if not configured
    """
    # Check if credentials already exist in session
    if 'user_oauth_credentials' in st.session_state:
        return st.session_state['user_oauth_credentials']

    with st.sidebar.expander("🔐 Yahoo OAuth Setup", expanded=True):
        st.markdown("""
        **Setup Instructions:**
        1. Go to [Yahoo Developer](https://developer.yahoo.com)
        2. Create an app and get your credentials
        3. Enter them below (stored only for this session)
        """)

        # Option 1: Manual input
        tab1, tab2 = st.tabs(["Manual Input", "JSON Upload"])

        with tab1:
            client_id = st.text_input(
                "Client ID",
                type="password",
                help="Your Yahoo App Client ID",
                key="oauth_client_id"
            )

            client_secret = st.text_input(
                "Client Secret",
                type="password",
                help="Your Yahoo App Client Secret",
                key="oauth_client_secret"
            )

            access_token = st.text_input(
                "Access Token",
                type="password",
                help="Your Yahoo OAuth Access Token",
                key="oauth_access_token"
            )

            refresh_token = st.text_input(
                "Refresh Token",
                type="password",
                help="Your Yahoo OAuth Refresh Token",
                key="oauth_refresh_token"
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Save Credentials", type="primary", use_container_width=True):
                    if all([client_id, client_secret, access_token, refresh_token]):
                        credentials = {
                            'client_id': client_id,
                            'client_secret': client_secret,
                            'access_token': access_token,
                            'refresh_token': refresh_token
                        }
                        st.session_state['user_oauth_credentials'] = credentials
                        st.success("✅ Credentials saved for this session!")
                        st.rerun()
                    else:
                        st.error("Please fill in all fields")

            with col2:
                if st.button("Clear All", use_container_width=True):
                    for key in ['oauth_client_id', 'oauth_client_secret',
                               'oauth_access_token', 'oauth_refresh_token']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()

        with tab2:
            st.markdown("Upload your `yahoo_oauth.json` file")

            uploaded_file = st.file_uploader(
                "Choose yahoo_oauth.json",
                type=['json'],
                help="Upload your Yahoo OAuth JSON file"
            )

            if uploaded_file is not None:
                try:
                    oauth_data = json.load(uploaded_file)

                    # Extract credentials based on common formats
                    credentials = {}

                    # Check for direct format
                    if 'consumer_key' in oauth_data:
                        credentials['client_id'] = oauth_data.get('consumer_key')
                        credentials['client_secret'] = oauth_data.get('consumer_secret')
                        credentials['access_token'] = oauth_data.get('access_token')
                        credentials['refresh_token'] = oauth_data.get('refresh_token',
                                                                   oauth_data.get('token_secret'))
                    # Check for nested format
                    elif 'client_id' in oauth_data:
                        credentials['client_id'] = oauth_data.get('client_id')
                        credentials['client_secret'] = oauth_data.get('client_secret')
                        credentials['access_token'] = oauth_data.get('access_token')
                        credentials['refresh_token'] = oauth_data.get('refresh_token')

                    if all(credentials.values()):
                        st.session_state['user_oauth_credentials'] = credentials
                        st.success("✅ Credentials loaded from file!")
                        st.rerun()
                    else:
                        st.error("Invalid OAuth file format")

                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")

        # Help section
        with st.expander("Need help?", expanded=False):
            st.markdown("""
            **To get OAuth credentials:**

            1. Visit https://developer.yahoo.com
            2. Create a new app
            3. Set redirect URI to `https://localhost:8080`
            4. Use the `generate_oauth_tokens.py` script:
               ```bash
               python generate_oauth_tokens.py
               ```
            5. Copy the generated credentials here

            **Security Note:**
            - Credentials are stored only in your browser session
            - They are never sent to our servers
            - They are cleared when you close the tab
            """)

    return None


def get_user_oauth_config() -> Optional[Dict[str, str]]:
    """
    Get user OAuth configuration from session state.

    Returns:
        OAuth credentials dict or None if not configured
    """
    return st.session_state.get('user_oauth_credentials')


def clear_user_oauth_config() -> None:
    """Clear user OAuth configuration from session state."""
    if 'user_oauth_credentials' in st.session_state:
        del st.session_state['user_oauth_credentials']

    # Clear individual input fields
    for key in ['oauth_client_id', 'oauth_client_secret',
               'oauth_access_token', 'oauth_refresh_token']:
        if key in st.session_state:
            del st.session_state[key]


def validate_oauth_config(config: Dict[str, str]) -> bool:
    """
    Validate OAuth configuration has all required fields.

    Args:
        config: OAuth configuration dictionary

    Returns:
        True if valid, False otherwise
    """
    required_fields = ['client_id', 'client_secret', 'access_token', 'refresh_token']
    return all(field in config and config[field] for field in required_fields)