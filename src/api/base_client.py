"""
Base API client with error handling, retry logic, and timeout management.
"""

import logging
import time
from typing import Dict, Any, Optional, Union
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..core.exceptions import (
    APIError, NetworkError, TimeoutError, RateLimitError,
    create_error_response
)
from ..core.constants import (
    MAX_API_RETRIES, API_REQUEST_TIMEOUT, RATE_LIMIT_DELAY,
    HTTP_STATUS_CODES
)


class BaseAPIClient:
    """
    Base class for API clients with common functionality.
    
    Provides:
    - Automatic retry logic with exponential backoff
    - Rate limiting protection
    - Timeout management
    - Structured error handling
    - Request/response logging
    """
    
    def __init__(
        self,
        base_url: str,
        timeout: int = API_REQUEST_TIMEOUT,
        max_retries: int = MAX_API_RETRIES,
        rate_limit_delay: float = RATE_LIMIT_DELAY,
        headers: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Initialize base API client.
        
        Args:
            base_url: Base URL for API endpoints
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            rate_limit_delay: Delay between retries in seconds
            headers: Default headers for requests
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.rate_limit_delay = rate_limit_delay
        
        # Set up logging
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize session with retry strategy
        self.session = self._create_session()
        
        # Set default headers
        self.default_headers = {
            'User-Agent': 'Yahoo-Fantasy-Baseball-Streamlit/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        if headers:
            self.default_headers.update(headers)
        
        # Rate limiting tracking
        self._last_request_time = 0.0
        self._request_count = 0
    
    def _create_session(self) -> requests.Session:
        """Create requests session with retry configuration."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1,
            raise_on_status=False
        )
        
        # Mount adapter with retry strategy
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _enforce_rate_limit(self) -> None:
        """Enforce rate limiting between requests."""
        current_time = time.time()
        time_since_last_request = current_time - self._last_request_time
        
        if time_since_last_request < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last_request
            self.logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self._last_request_time = time.time()
        self._request_count += 1
    
    def _prepare_url(self, endpoint: str) -> str:
        """Prepare full URL from endpoint."""
        if endpoint.startswith(('http://', 'https://')):
            return endpoint
        
        endpoint = endpoint.lstrip('/')
        return f"{self.base_url}/{endpoint}"
    
    def _prepare_headers(self, headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Prepare request headers."""
        request_headers = self.default_headers.copy()
        if headers:
            request_headers.update(headers)
        return request_headers
    
    def _handle_response(self, response: requests.Response, endpoint: str) -> Dict[str, Any]:
        """
        Handle API response and convert to standardized format.
        
        Args:
            response: HTTP response object
            endpoint: API endpoint that was called
            
        Returns:
            Parsed response data
            
        Raises:
            APIError: For various API error conditions
        """
        # Log response details
        self.logger.debug(
            f"Response: {response.status_code} for {endpoint} "
            f"(took {response.elapsed.total_seconds():.2f}s)"
        )
        
        # Handle rate limiting
        if response.status_code == HTTP_STATUS_CODES["TOO_MANY_REQUESTS"]:
            retry_after = int(response.headers.get('Retry-After', 60))
            raise RateLimitError(
                f"Rate limit exceeded for {endpoint}",
                retry_after=retry_after,
                status_code=response.status_code
            )
        
        # Handle client errors (4xx)
        if 400 <= response.status_code < 500:
            error_msg = f"Client error {response.status_code} for {endpoint}"
            try:
                error_data = response.json()
                if 'error' in error_data:
                    error_msg += f": {error_data['error']}"
            except (ValueError, KeyError):
                error_msg += f": {response.text[:200]}"
            
            raise APIError(error_msg, response.status_code, {"response_text": response.text})
        
        # Handle server errors (5xx)
        if response.status_code >= 500:
            error_msg = f"Server error {response.status_code} for {endpoint}"
            raise APIError(error_msg, response.status_code, {"response_text": response.text})
        
        # Handle successful responses
        if response.status_code == HTTP_STATUS_CODES["OK"]:
            try:
                return response.json()
            except ValueError as e:
                self.logger.warning(f"Failed to parse JSON response from {endpoint}: {e}")
                return {"raw_response": response.text}
        
        # Handle other successful status codes
        return {"status_code": response.status_code, "response": response.text}
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request with error handling and retries.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Query parameters
            data: Request body data
            headers: Additional headers
            timeout: Request timeout override
            
        Returns:
            Parsed response data
            
        Raises:
            NetworkError: For network-related errors
            TimeoutError: For timeout errors
            APIError: For API-specific errors
        """
        url = self._prepare_url(endpoint)
        request_headers = self._prepare_headers(headers)
        request_timeout = timeout or self.timeout
        
        # Enforce rate limiting
        self._enforce_rate_limit()
        
        # Log request details
        self.logger.debug(f"Making {method} request to {url}")
        if params:
            self.logger.debug(f"Query params: {params}")
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=request_headers,
                timeout=request_timeout
            )
            
            return self._handle_response(response, endpoint)
            
        except requests.exceptions.Timeout as e:
            error_msg = f"Request timeout after {request_timeout}s for {endpoint}"
            self.logger.error(error_msg)
            raise TimeoutError(error_msg, e)
        
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Connection error for {endpoint}"
            self.logger.error(f"{error_msg}: {e}")
            raise NetworkError(error_msg, e)
        
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed for {endpoint}"
            self.logger.error(f"{error_msg}: {e}")
            raise NetworkError(error_msg, e)
    
    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """Make GET request."""
        return self._make_request("GET", endpoint, params=params, headers=headers, timeout=timeout)
    
    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """Make POST request."""
        return self._make_request("POST", endpoint, params=params, data=data, headers=headers, timeout=timeout)
    
    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """Make PUT request."""
        return self._make_request("PUT", endpoint, params=params, data=data, headers=headers, timeout=timeout)
    
    def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """Make DELETE request."""
        return self._make_request("DELETE", endpoint, params=params, headers=headers, timeout=timeout)
    
    def health_check(self) -> bool:
        """
        Perform basic health check on the API.
        
        Returns:
            True if API is accessible
        """
        try:
            # Try a simple request to the base URL
            response = self.session.get(self.base_url, timeout=5)
            return response.status_code < 500
        except Exception as e:
            self.logger.warning(f"Health check failed: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics."""
        return {
            "base_url": self.base_url,
            "request_count": self._request_count,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "rate_limit_delay": self.rate_limit_delay
        }
    
    def close(self) -> None:
        """Close the session and clean up resources."""
        if self.session:
            self.session.close()
            self.logger.debug("API client session closed")