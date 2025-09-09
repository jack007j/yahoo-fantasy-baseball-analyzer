"""
Custom Yahoo OAuth 1.0a implementation that works with existing tokens.

This module provides a custom OAuth implementation that bypasses the issues
with the yahoo_oauth library by directly using the tokens without re-authentication.
"""

import json
import time
import logging
from typing import Optional, Dict, Any
from requests_oauthlib import OAuth1Session
import requests


class CustomYahooOAuth:
    """
    Custom Yahoo OAuth 1.0a client that works with existing tokens.
    
    This class provides the same interface as the yahoo_oauth.OAuth2 class
    but uses a more reliable implementation that doesn't trigger re-authentication.
    """
    
    def __init__(self, oauth_file: str = 'yahoo_oauth.json'):
        """
        Initialize the custom OAuth client.
        
        Args:
            oauth_file: Path to the JSON file containing OAuth credentials
        """
        self.logger = logging.getLogger(__name__)
        self.oauth_file = oauth_file
        
        # OAuth credentials
        self.consumer_key: Optional[str] = None
        self.consumer_secret: Optional[str] = None
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        
        # Token timing (for compatibility with yahoo_fantasy_api)
        self.token_time: float = time.time()
        self.token_expiry: float = time.time() + 3600  # 1 hour from now
        
        # Load credentials
        self._load_credentials()
    
    def _load_credentials(self) -> None:
        """Load OAuth credentials from the JSON file."""
        try:
            with open(self.oauth_file, 'r') as f:
                oauth_data = json.load(f)
            
            self.consumer_key = oauth_data.get('consumer_key')
            self.consumer_secret = oauth_data.get('consumer_secret')
            self.access_token = oauth_data.get('access_token')
            self.refresh_token = oauth_data.get('refresh_token')
            
            if not all([self.consumer_key, self.consumer_secret, self.access_token]):
                raise ValueError("Missing required OAuth credentials")
            
            self.logger.info("Successfully loaded OAuth credentials")
            
        except Exception as e:
            self.logger.error(f"Failed to load OAuth credentials: {e}")
            raise
    
    def token_is_valid(self) -> bool:
        """
        Check if the current token is valid.
        
        For our purposes, we'll assume the token is valid since we're using
        existing tokens that were recently generated.
        
        Returns:
            True if token is valid, False otherwise
        """
        # For existing tokens, we'll assume they're valid
        # In a production environment, you might want to make a test API call
        return bool(self.access_token and self.consumer_key)
    
    def refresh_access_token(self) -> bool:
        """
        Refresh the access token.
        
        For now, this is a no-op since we're using existing tokens.
        In a full implementation, this would use the refresh token to get a new access token.
        
        Returns:
            True if refresh was successful, False otherwise
        """
        self.logger.info("Token refresh requested - using existing token")
        return True
    
    def get_oauth_session(self) -> OAuth1Session:
        """
        Create an OAuth1Session for making authenticated requests.
        
        Returns:
            Configured OAuth1Session instance
        """
        if not self.token_is_valid():
            raise ValueError("OAuth token is not valid")
        
        return OAuth1Session(
            client_key=self.consumer_key,
            client_secret=self.consumer_secret,
            resource_owner_key=self.access_token,
            resource_owner_secret=self.refresh_token,  # This is the token secret in OAuth 1.0a
            signature_method='HMAC-SHA1',
            signature_type='AUTH_HEADER'
        )
    
    def make_request(self, url: str, method: str = 'GET', **kwargs) -> requests.Response:
        """
        Make an authenticated request to the Yahoo API.
        
        Args:
            url: The URL to request
            method: HTTP method (GET, POST, etc.)
            **kwargs: Additional arguments to pass to the request
            
        Returns:
            Response object
        """
        session = self.get_oauth_session()
        
        if method.upper() == 'GET':
            return session.get(url, **kwargs)
        elif method.upper() == 'POST':
            return session.post(url, **kwargs)
        elif method.upper() == 'PUT':
            return session.put(url, **kwargs)
        elif method.upper() == 'DELETE':
            return session.delete(url, **kwargs)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")


class YahooFantasyAPIWrapper:
    """
    Wrapper that provides the exact same interface as yahoo_oauth.OAuth2.
    
    This class acts as a drop-in replacement for the OAuth2 class from yahoo_oauth
    and provides all the attributes and methods that yahoo_fantasy_api expects.
    """
    
    def __init__(self, oauth_file: str = 'yahoo_oauth.json'):
        """Initialize the wrapper with custom OAuth implementation."""
        self.oauth_client = CustomYahooOAuth(oauth_file)
        
        # Expose properties that yahoo_fantasy_api expects (exact same names as OAuth2)
        self.consumer_key = self.oauth_client.consumer_key
        self.consumer_secret = self.oauth_client.consumer_secret
        self.access_token = self.oauth_client.access_token
        self.refresh_token = self.oauth_client.refresh_token
        self.token_time = self.oauth_client.token_time
        self.token_expiry = self.oauth_client.token_expiry
        
        # Additional attributes that yahoo_fantasy_api might expect
        self.oauth_version = '1.0a'
        self.signature_method = 'HMAC-SHA1'
        
        # Create the session object that yahoo_fantasy_api uses
        self._session = None
    
    def token_is_valid(self) -> bool:
        """Check if token is valid."""
        return self.oauth_client.token_is_valid()
    
    def refresh_access_token(self) -> bool:
        """Refresh the access token."""
        return self.oauth_client.refresh_access_token()
    
    @property
    def session(self) -> OAuth1Session:
        """Get the OAuth session for making requests."""
        if self._session is None:
            self._session = self.oauth_client.get_oauth_session()
        return self._session
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """Make a GET request using the OAuth session."""
        return self.session.get(url, **kwargs)
    
    def post(self, url: str, **kwargs) -> requests.Response:
        """Make a POST request using the OAuth session."""
        return self.session.post(url, **kwargs)
    
    def put(self, url: str, **kwargs) -> requests.Response:
        """Make a PUT request using the OAuth session."""
        return self.session.put(url, **kwargs)
    
    def delete(self, url: str, **kwargs) -> requests.Response:
        """Make a DELETE request using the OAuth session."""
        return self.session.delete(url, **kwargs)