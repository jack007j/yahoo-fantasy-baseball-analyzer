"""
Text processing utilities for the Yahoo Fantasy Baseball application.
"""

import re
import unicodedata
from typing import Optional


def slugify(value: Optional[str]) -> str:
    """
    Convert a string to a URL-safe slug for player name matching.
    
    This function normalizes player names for consistent matching between
    Yahoo Fantasy API and MLB Stats API data.
    
    Args:
        value: Input string to slugify
        
    Returns:
        Normalized slug string
        
    Examples:
        >>> slugify("José Altuve")
        'jose-altuve'
        >>> slugify("Mike Trout Jr.")
        'mike-trout-jr'
        >>> slugify(None)
        ''
    """
    if value is None:
        return ""
    
    # Convert to string and normalize Unicode characters
    value = str(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    
    # Remove non-alphanumeric characters except spaces and hyphens
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    
    # Replace spaces and multiple hyphens with single hyphens
    value = re.sub(r'[-\s]+', '-', value)
    
    return value


def normalize_player_name(name: Optional[str]) -> str:
    """
    Normalize player name for matching purposes.
    
    Args:
        name: Player name to normalize
        
    Returns:
        Normalized name string
    """
    if not name:
        return ""
    
    # Remove common suffixes
    name = re.sub(r'\s+(Jr\.?|Sr\.?|III?|IV)$', '', name, flags=re.IGNORECASE)
    
    # Normalize spacing
    name = re.sub(r'\s+', ' ', name.strip())
    
    return slugify(name)


def extract_first_last_name(full_name: str) -> tuple[str, str]:
    """
    Extract first and last name from full name.
    
    Args:
        full_name: Full player name
        
    Returns:
        Tuple of (first_name, last_name)
    """
    if not full_name:
        return "", ""
    
    parts = full_name.strip().split()
    if len(parts) == 1:
        return parts[0], ""
    elif len(parts) == 2:
        return parts[0], parts[1]
    else:
        # For names with middle names/initials, take first and last
        return parts[0], parts[-1]


def calculate_name_similarity(name1: str, name2: str) -> float:
    """
    Calculate similarity between two player names.
    
    Uses a simple character-based similarity metric.
    
    Args:
        name1: First name to compare
        name2: Second name to compare
        
    Returns:
        Similarity score between 0.0 and 1.0
    """
    if not name1 or not name2:
        return 0.0
    
    # Normalize both names
    norm1 = normalize_player_name(name1)
    norm2 = normalize_player_name(name2)
    
    if norm1 == norm2:
        return 1.0
    
    # Simple character overlap calculation
    set1 = set(norm1.replace('-', ''))
    set2 = set(norm2.replace('-', ''))
    
    if not set1 or not set2:
        return 0.0
    
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    return intersection / union if union > 0 else 0.0


def format_player_display_name(name: str, positions: list[str]) -> str:
    """
    Format player name for display with positions.
    
    Args:
        name: Player name
        positions: List of eligible positions
        
    Returns:
        Formatted display string
    """
    if not name:
        return "Unknown Player"
    
    if not positions:
        return name
    
    # Filter out 'P' position for display
    display_positions = [pos for pos in positions if pos != 'P']
    
    if display_positions:
        pos_str = '/'.join(display_positions)
        return f"{name} ({pos_str})"
    
    return name


def clean_team_name(team_name: str) -> str:
    """
    Clean and normalize team name.
    
    Args:
        team_name: Raw team name
        
    Returns:
        Cleaned team name
    """
    if not team_name:
        return "Unknown Team"
    
    # Remove common prefixes/suffixes
    cleaned = re.sub(r'^(The\s+)', '', team_name, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s+(Baseball\s+Club|FC|Baseball)$', '', cleaned, flags=re.IGNORECASE)
    
    return cleaned.strip()


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate text to specified length with suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add when truncating
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def format_percentage(value: float, decimal_places: int = 1) -> str:
    """
    Format a float as a percentage string.
    
    Args:
        value: Float value (0.0 to 100.0)
        decimal_places: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    return f"{value:.{decimal_places}f}%"


def parse_yahoo_id(yahoo_id: str) -> dict[str, str]:
    """
    Parse Yahoo Fantasy player ID into components.
    
    Args:
        yahoo_id: Yahoo Fantasy player ID (e.g., "458.p.12345")
        
    Returns:
        Dictionary with parsed components
    """
    if not yahoo_id:
        return {}
    
    parts = yahoo_id.split('.')
    if len(parts) >= 3:
        return {
            "game_id": parts[0],
            "type": parts[1], 
            "player_id": parts[2]
        }
    
    return {"raw_id": yahoo_id}