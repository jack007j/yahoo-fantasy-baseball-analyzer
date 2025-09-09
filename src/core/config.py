"""
Configuration management for the Yahoo Fantasy Baseball application.
"""

import logging
import re
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, validator
import streamlit as st

from .constants import (
    YAHOO_LEAGUE_ID_PATTERN,
    YAHOO_TEAM_KEY_PATTERN,
    DEFAULT_CACHE_TTL_SECONDS,
    MAX_API_RETRIES,
    API_REQUEST_TIMEOUT,
    ERROR_MESSAGES
)
from .exceptions import ConfigurationError


class YahooOAuthConfig(BaseModel):
    """Yahoo OAuth configuration model."""
    
    client_id: str = Field(..., description="Yahoo OAuth client ID")
    client_secret: str = Field(..., description="Yahoo OAuth client secret")
    access_token: str = Field(..., description="Yahoo OAuth access token")
    refresh_token: str = Field(..., description="Yahoo OAuth refresh token")
    
    @validator('client_id', 'client_secret', 'access_token', 'refresh_token')
    def validate_not_empty(cls, v: str) -> str:
        """Ensure OAuth values are not empty."""
        if not v or not v.strip():
            raise ValueError("OAuth configuration values cannot be empty")
        return v.strip()


class AppConfig(BaseModel):
    """Main application configuration."""
    
    # League and team configuration
    default_league_id: str = Field(..., description="Default Yahoo Fantasy league ID")
    default_team_key: str = Field(..., description="Default Yahoo Fantasy team key")
    
    # API configuration
    cache_ttl_seconds: int = Field(DEFAULT_CACHE_TTL_SECONDS, ge=60, le=86400, 
                                  description="Cache TTL in seconds")
    max_retries: int = Field(MAX_API_RETRIES, ge=1, le=10, 
                           description="Maximum API retry attempts")
    request_timeout: int = Field(API_REQUEST_TIMEOUT, ge=5, le=60, 
                               description="API request timeout in seconds")
    
    # Analysis configuration
    analysis_days_ahead: int = Field(10, ge=1, le=30, 
                                   description="Days ahead to analyze")
    ownership_threshold: float = Field(50.0, ge=0.0, le=100.0, 
                                     description="Ownership percentage threshold")
    
    @validator('default_league_id')
    def validate_league_id(cls, v: str) -> str:
        """Validate Yahoo Fantasy league ID format."""
        if not re.match(YAHOO_LEAGUE_ID_PATTERN, v):
            raise ValueError(f"Invalid league ID format: {v}")
        return v
    
    @validator('default_team_key')
    def validate_team_key(cls, v: str) -> str:
        """Validate Yahoo Fantasy team key format."""
        if not re.match(YAHOO_TEAM_KEY_PATTERN, v):
            raise ValueError(f"Invalid team key format: {v}")
        return v


class LoggingConfig(BaseModel):
    """Logging configuration."""
    
    level: str = Field("INFO", description="Logging level")
    format: str = Field("%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
                       description="Log format string")
    
    @validator('level')
    def validate_log_level(cls, v: str) -> str:
        """Validate logging level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return v_upper


class ApplicationConfiguration:
    """
    Main configuration manager for the application.
    
    Handles loading configuration from Streamlit secrets and provides
    validated configuration objects for different parts of the application.
    """
    
    def __init__(self) -> None:
        """Initialize configuration from Streamlit secrets."""
        self._yahoo_oauth: Optional[YahooOAuthConfig] = None
        self._app_config: Optional[AppConfig] = None
        self._logging_config: Optional[LoggingConfig] = None
        self._load_configuration()
    
    def _load_configuration(self) -> None:
        """Load and validate configuration from Streamlit secrets."""
        try:
            # Check if secrets are available
            if not hasattr(st, 'secrets') or not st.secrets:
                raise ConfigurationError(ERROR_MESSAGES["NO_OAUTH_CONFIG"])
            
            # Load Yahoo OAuth configuration
            if "yahoo_oauth" not in st.secrets:
                raise ConfigurationError("Yahoo OAuth configuration missing from secrets")
            
            oauth_data = dict(st.secrets["yahoo_oauth"])
            self._yahoo_oauth = YahooOAuthConfig(**oauth_data)
            
            # Load app configuration
            app_data = dict(st.secrets.get("app_config", {}))
            
            # Set defaults if not provided
            if "default_league_id" not in app_data:
                app_data["default_league_id"] = "458.l.135626"  # Example default
            if "default_team_key" not in app_data:
                app_data["default_team_key"] = "458.l.135626.t.6"  # Example default
            
            self._app_config = AppConfig(**app_data)
            
            # Load logging configuration
            logging_data = dict(st.secrets.get("logging", {}))
            self._logging_config = LoggingConfig(**logging_data)
            
        except Exception as e:
            if isinstance(e, ConfigurationError):
                raise
            raise ConfigurationError(f"Failed to load configuration: {str(e)}")
    
    @property
    def yahoo_oauth(self) -> YahooOAuthConfig:
        """Get Yahoo OAuth configuration."""
        if self._yahoo_oauth is None:
            raise ConfigurationError("Yahoo OAuth configuration not loaded")
        return self._yahoo_oauth
    
    @property
    def app_config(self) -> AppConfig:
        """Get application configuration."""
        if self._app_config is None:
            raise ConfigurationError("Application configuration not loaded")
        return self._app_config
    
    @property
    def logging_config(self) -> LoggingConfig:
        """Get logging configuration."""
        if self._logging_config is None:
            raise ConfigurationError("Logging configuration not loaded")
        return self._logging_config
    
    def get_yahoo_oauth_dict(self) -> Dict[str, str]:
        """Get Yahoo OAuth configuration as dictionary."""
        return self.yahoo_oauth.dict()
    
    def get_app_config_dict(self) -> Dict[str, Any]:
        """Get application configuration as dictionary."""
        return self.app_config.dict()
    
    def validate_league_and_team(self, league_id: str, team_key: str) -> bool:
        """
        Validate league ID and team key formats.
        
        Args:
            league_id: Yahoo Fantasy league ID
            team_key: Yahoo Fantasy team key
            
        Returns:
            True if both are valid
            
        Raises:
            ConfigurationError: If validation fails
        """
        if not re.match(YAHOO_LEAGUE_ID_PATTERN, league_id):
            raise ConfigurationError(f"Invalid league ID format: {league_id}")
        
        if not re.match(YAHOO_TEAM_KEY_PATTERN, team_key):
            raise ConfigurationError(f"Invalid team key format: {team_key}")
        
        # Verify team key belongs to league
        league_part = team_key.split('.t.')[0]
        if league_part != league_id:
            raise ConfigurationError(f"Team key {team_key} does not belong to league {league_id}")
        
        return True
    
    def setup_logging(self) -> None:
        """Configure application logging."""
        logging.basicConfig(
            level=getattr(logging, self.logging_config.level),
            format=self.logging_config.format,
            force=True
        )
        
        # Set specific logger levels
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("streamlit").setLevel(logging.WARNING)


# Global configuration instance
_config_instance: Optional[ApplicationConfiguration] = None


def get_config() -> ApplicationConfiguration:
    """
    Get the global configuration instance.
    
    Returns:
        ApplicationConfiguration instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = ApplicationConfiguration()
    return _config_instance


def reload_config() -> ApplicationConfiguration:
    """
    Reload configuration from Streamlit secrets.
    
    Returns:
        New ApplicationConfiguration instance
    """
    global _config_instance
    _config_instance = ApplicationConfiguration()
    return _config_instance


# Note: AppConfig class is defined above at line 38
# Use get_config() function to get ApplicationConfiguration instance