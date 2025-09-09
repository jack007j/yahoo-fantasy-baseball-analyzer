"""
Application constants for the Yahoo Fantasy Baseball application.
"""

from typing import Dict, List

# API Configuration
YAHOO_FANTASY_BASE_URL = "https://fantasysports.yahooapis.com/fantasy/v2"
MLB_STATS_BASE_URL = "https://statsapi.mlb.com/api/v1"
BASEBALL_SAVANT_BASE_URL = "https://baseballsavant.mlb.com/savant-player"

# Yahoo Fantasy API Constants
YAHOO_GAME_CODE = "mlb"
YAHOO_CURRENT_SEASON = 2024

# MLB API Constants
MLB_SPORT_ID = 1  # MLB sport ID in MLB Stats API

# Fantasy Baseball Positions
PITCHER_POSITIONS = {"SP", "RP", "P"}
POSITION_PLAYERS = {"C", "CA", "1B", "2B", "3B", "SS", "OF", "LF", "CF", "RF", "DH"}
ALL_POSITIONS = PITCHER_POSITIONS | POSITION_PLAYERS

# Position Display Order
POSITION_ORDER = ["C", "CA", "1B", "2B", "3B", "SS", "OF", "LF", "CF", "RF", "DH", "SP", "RP", "P"]

# Fantasy Week Configuration
FANTASY_WEEK_START_DAY = 0  # Monday (0=Monday, 6=Sunday)
FANTASY_WEEK_LENGTH_DAYS = 7
TARGET_ANALYSIS_DAYS = ["Monday", "Tuesday"]

# Analysis Configuration
DEFAULT_CACHE_TTL_SECONDS = 3600  # 1 hour
MAX_API_RETRIES = 3
API_REQUEST_TIMEOUT = 10
RATE_LIMIT_DELAY = 2  # seconds between retries

# Second Start Analysis
MIN_GAMES_FOR_SECOND_START = 5
SECOND_START_ANALYSIS_BUFFER_DAYS = 5

# Player Matching
PLAYER_NAME_SIMILARITY_THRESHOLD = 0.8
MAX_PLAYER_MATCH_ATTEMPTS = 3

# UI Configuration
DEFAULT_PAGE_SIZE = 50
MAX_DISPLAY_PLAYERS = 100

# Streamlit Configuration
STREAMLIT_THEME = {
    "primaryColor": "#1f77b4",
    "backgroundColor": "#ffffff", 
    "secondaryBackgroundColor": "#f0f2f6",
    "textColor": "#262730"
}

# Error Messages
ERROR_MESSAGES: Dict[str, str] = {
    "NO_OAUTH_CONFIG": "Yahoo OAuth configuration not found in Streamlit secrets",
    "INVALID_LEAGUE_ID": "Invalid Yahoo Fantasy league ID format",
    "INVALID_TEAM_KEY": "Invalid Yahoo Fantasy team key format",
    "API_UNAVAILABLE": "External API service is currently unavailable",
    "NO_PITCHERS_FOUND": "No pitchers found matching the analysis criteria",
    "ANALYSIS_TIMEOUT": "Analysis timed out - please try again",
    "CACHE_ERROR": "Error accessing cached data",
    "NETWORK_ERROR": "Network connection error - please check your internet connection"
}

# Success Messages
SUCCESS_MESSAGES: Dict[str, str] = {
    "ANALYSIS_COMPLETE": "Analysis completed successfully",
    "DATA_REFRESHED": "Data refreshed from APIs",
    "CACHE_CLEARED": "Cache cleared successfully",
    "CONFIG_LOADED": "Configuration loaded successfully"
}

# Logging Configuration
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# File Extensions
ALLOWED_CONFIG_EXTENSIONS = {".toml", ".json", ".yaml", ".yml"}

# Validation Patterns
YAHOO_LEAGUE_ID_PATTERN = r"^\d+\.l\.\d+$"
YAHOO_TEAM_KEY_PATTERN = r"^\d+\.l\.\d+\.t\.\d+$"
MLB_PLAYER_ID_PATTERN = r"^\d+$"

# Default Values
DEFAULT_OWNERSHIP_THRESHOLD = 50.0  # Percentage
DEFAULT_ANALYSIS_DAYS_AHEAD = 10
DEFAULT_MAX_WAIVER_PLAYERS = 100

# API Rate Limits (requests per minute)
YAHOO_API_RATE_LIMIT = 1000
MLB_API_RATE_LIMIT = 2000

# Cache Keys
CACHE_KEYS = {
    "TEAM_SCHEDULE": "team_schedule_{team_id}_{start_date}_{end_date}",
    "PROBABLE_STARTERS": "probable_starters_{start_date}_{end_date}",
    "WAIVER_PLAYERS": "waiver_players_{league_id}",
    "TEAM_ROSTER": "team_roster_{team_key}",
    "LEAGUE_INFO": "league_info_{league_id}",
    "PLAYER_STATS": "player_stats_{player_id}"
}

# HTTP Status Codes
HTTP_STATUS_CODES = {
    "OK": 200,
    "CREATED": 201,
    "BAD_REQUEST": 400,
    "UNAUTHORIZED": 401,
    "FORBIDDEN": 403,
    "NOT_FOUND": 404,
    "TOO_MANY_REQUESTS": 429,
    "INTERNAL_SERVER_ERROR": 500,
    "BAD_GATEWAY": 502,
    "SERVICE_UNAVAILABLE": 503
}

# Fantasy Categories (for future expansion)
FANTASY_CATEGORIES = {
    "BATTING": ["R", "HR", "RBI", "SB", "AVG"],
    "PITCHING": ["W", "SV", "K", "ERA", "WHIP"]
}

# Team Abbreviations to Full Names (common MLB teams)
MLB_TEAM_NAMES: Dict[str, str] = {
    "LAA": "Los Angeles Angels",
    "HOU": "Houston Astros", 
    "OAK": "Oakland Athletics",
    "TOR": "Toronto Blue Jays",
    "ATL": "Atlanta Braves",
    "MIL": "Milwaukee Brewers",
    "STL": "St. Louis Cardinals",
    "CHC": "Chicago Cubs",
    "ARI": "Arizona Diamondbacks",
    "LAD": "Los Angeles Dodgers",
    "SF": "San Francisco Giants",
    "CLE": "Cleveland Guardians",
    "SEA": "Seattle Mariners",
    "MIA": "Miami Marlins",
    "NYM": "New York Mets",
    "WSH": "Washington Nationals",
    "BAL": "Baltimore Orioles",
    "SD": "San Diego Padres",
    "PHI": "Philadelphia Phillies",
    "PIT": "Pittsburgh Pirates",
    "TEX": "Texas Rangers",
    "TB": "Tampa Bay Rays",
    "BOS": "Boston Red Sox",
    "CIN": "Cincinnati Reds",
    "COL": "Colorado Rockies",
    "KC": "Kansas City Royals",
    "DET": "Detroit Tigers",
    "MIN": "Minnesota Twins",
    "CWS": "Chicago White Sox",
    "NYY": "New York Yankees"
}