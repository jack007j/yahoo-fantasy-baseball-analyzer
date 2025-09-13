"""
User-specific Yahoo OAuth implementation for multi-user deployment.

This module provides OAuth functionality that accepts user-provided credentials
instead of using shared app credentials.
"""

import logging
from typing import Dict, Optional, Any
from requests_oauthlib import OAuth1Session
import streamlit as st

from ..core.exceptions import AuthenticationError


class UserYahooOAuth:
    """
    Yahoo OAuth client that uses user-provided credentials.

    This implementation stores credentials in session state only,
    ensuring proper isolation between users.
    """

    YAHOO_BASE_URL = "https://fantasysports.yahooapis.com/fantasy/v2"

    def __init__(self, user_credentials: Optional[Dict[str, str]] = None) -> None:
        """
        Initialize OAuth client with user credentials.

        Args:
            user_credentials: Dictionary containing OAuth credentials
                             If None, attempts to load from session state
        """
        self.logger = logging.getLogger(__name__)

        # Try to get credentials from parameter or session state
        if user_credentials:
            self.credentials = user_credentials
        else:
            self.credentials = st.session_state.get('user_oauth_credentials')

        if not self.credentials:
            raise AuthenticationError(
                "No OAuth credentials provided. Please configure in the sidebar."
            )

        # Validate credentials
        required_fields = ['client_id', 'client_secret', 'access_token', 'refresh_token']
        missing = [f for f in required_fields if f not in self.credentials or not self.credentials[f]]

        if missing:
            raise AuthenticationError(
                f"Missing OAuth credentials: {', '.join(missing)}"
            )

        # Store credentials (never in instance variables for security)
        self._init_session()

    def _init_session(self) -> None:
        """Initialize OAuth session with user credentials."""
        try:
            self.session = OAuth1Session(
                client_key=self.credentials['client_id'],
                client_secret=self.credentials['client_secret'],
                resource_owner_key=self.credentials['access_token'],
                resource_owner_secret=self.credentials['refresh_token'],
                signature_method='HMAC-SHA1'
            )
        except Exception as e:
            raise AuthenticationError(f"Failed to initialize OAuth session: {str(e)}")

    def token_is_valid(self) -> bool:
        """
        Check if the current token is valid.

        Returns:
            True if token is valid
        """
        try:
            # Test with a simple API call
            response = self.session.get(f"{self.YAHOO_BASE_URL}/game/mlb")
            return response.status_code == 200
        except Exception as e:
            self.logger.warning(f"Token validation failed: {e}")
            return False

    def refresh_access_token(self) -> bool:
        """
        Attempt to refresh the access token.

        For user-provided tokens, this typically requires them to
        regenerate tokens manually.

        Returns:
            False (users must refresh manually)
        """
        # User tokens can't be refreshed automatically in this implementation
        # They need to generate new tokens using the generate_oauth_tokens.py script
        st.warning(
            "Token refresh required. Please generate new tokens using the "
            "generate_oauth_tokens.py script and update your credentials."
        )
        return False

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make authenticated GET request to Yahoo API.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            JSON response data

        Raises:
            AuthenticationError: If request fails
        """
        url = f"{self.YAHOO_BASE_URL}/{endpoint}"

        try:
            response = self.session.get(url, params=params)

            if response.status_code == 401:
                # Token might be expired
                st.error("Authentication failed. Please check your OAuth credentials.")
                raise AuthenticationError("Yahoo OAuth token expired or invalid")

            response.raise_for_status()
            return response.json()

        except Exception as e:
            if isinstance(e, AuthenticationError):
                raise
            raise AuthenticationError(f"API request failed: {str(e)}")


class UserOAuth2Wrapper:
    """
    Wrapper class that mimics yahoo_oauth.OAuth2 interface
    but uses user-provided credentials.
    """

    def __init__(self, user_credentials: Optional[Dict[str, str]] = None) -> None:
        """Initialize wrapper with user credentials."""
        self.oauth_client = UserYahooOAuth(user_credentials)

        # Properties for compatibility
        self.consumer_key = self.oauth_client.credentials.get('client_id')
        self.consumer_secret = self.oauth_client.credentials.get('client_secret')
        self.access_token = self.oauth_client.credentials.get('access_token')
        self.refresh_token = self.oauth_client.credentials.get('refresh_token')
        self.token_time = 0.0
        self.access_token_lifetime = 3600

    def token_is_valid(self) -> bool:
        """Check if token is valid."""
        return self.oauth_client.token_is_valid()

    def refresh_access_token(self) -> bool:
        """Refresh access token."""
        return self.oauth_client.refresh_access_token()

    def session(self) -> OAuth1Session:
        """Get OAuth session."""
        return self.oauth_client.session


def get_user_oauth_client() -> Optional[UserOAuth2Wrapper]:
    """
    Get user-specific OAuth client from session state.

    Returns:
        OAuth client or None if not configured
    """
    credentials = st.session_state.get('user_oauth_credentials')

    if not credentials:
        return None

    try:
        return UserOAuth2Wrapper(credentials)
    except Exception as e:
        st.error(f"Failed to initialize OAuth client: {str(e)}")
        return None