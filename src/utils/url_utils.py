"""
URL utility functions for Yahoo Fantasy Baseball application.

Provides functions for creating external links and URLs.
"""

import re
import unicodedata
from typing import Optional


def create_baseball_savant_url(player_name: str, mlb_player_id: int) -> str:
    """
    Create Baseball Savant URL for a player.
    
    Args:
        player_name: Player's full name
        mlb_player_id: MLB Stats API player ID
        
    Returns:
        Baseball Savant URL for the player
    """
    if not player_name or not mlb_player_id:
        return ""
    
    try:
        # Convert to int to ensure it's valid
        player_id = int(mlb_player_id)
        
        # Create URL-friendly slug from name
        name_slug = slugify(player_name)
        
        return f"https://baseballsavant.mlb.com/savant-player/{name_slug}-{player_id}"
    
    except (ValueError, TypeError):
        return ""


def slugify(value: str) -> str:
    """
    Convert a string to a URL-friendly slug.
    
    Args:
        value: String to convert
        
    Returns:
        URL-friendly slug
    """
    if not value:
        return ""
    
    # Convert to string and normalize unicode
    value = str(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    
    # Remove non-alphanumeric characters except spaces and hyphens
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    
    # Replace spaces and multiple hyphens with single hyphens
    value = re.sub(r'[-\s]+', '-', value)
    
    return value


def create_yahoo_fantasy_url(team_key: str) -> str:
    """
    Create Yahoo Fantasy Baseball team URL.
    
    Args:
        team_key: Yahoo Fantasy team key (e.g., '458.l.135626.t.6')
        
    Returns:
        Yahoo Fantasy team URL
    """
    if not team_key:
        return ""
    
    return f"https://baseball.fantasysports.yahoo.com/b1/{team_key}"


def create_mlb_player_url(mlb_player_id: int) -> str:
    """
    Create MLB.com player URL.
    
    Args:
        mlb_player_id: MLB Stats API player ID
        
    Returns:
        MLB.com player URL
    """
    if not mlb_player_id:
        return ""
    
    try:
        player_id = int(mlb_player_id)
        return f"https://www.mlb.com/player/{player_id}"
    except (ValueError, TypeError):
        return ""


def create_fangraphs_url(player_name: str) -> str:
    """
    Create FanGraphs search URL for a player.
    
    Args:
        player_name: Player's full name
        
    Returns:
        FanGraphs search URL
    """
    if not player_name:
        return ""
    
    # URL encode the player name for search
    import urllib.parse
    encoded_name = urllib.parse.quote_plus(player_name)
    
    return f"https://www.fangraphs.com/players.aspx?lastname={encoded_name}"


def validate_url(url: str) -> bool:
    """
    Validate if a string is a properly formatted URL.
    
    Args:
        url: URL string to validate
        
    Returns:
        True if URL is valid, False otherwise
    """
    if not url:
        return False
    
    # Basic URL pattern matching
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(url_pattern.match(url))


def extract_team_key_from_url(url: str) -> Optional[str]:
    """
    Extract team key from Yahoo Fantasy URL.
    
    Args:
        url: Yahoo Fantasy URL
        
    Returns:
        Team key if found, None otherwise
    """
    if not url:
        return None
    
    # Pattern to match team key in Yahoo Fantasy URLs
    pattern = r'(\d+\.l\.\d+\.t\.\d+)'
    match = re.search(pattern, url)
    
    return match.group(1) if match else None


def create_external_link(url: str, text: str, new_tab: bool = True) -> str:
    """
    Create HTML for an external link.
    
    Args:
        url: Link URL
        text: Link text
        new_tab: Whether to open in new tab
        
    Returns:
        HTML string for the link
    """
    if not url or not text:
        return text
    
    target = ' target="_blank"' if new_tab else ''
    return f'<a href="{url}"{target}>{text}</a>'


def is_baseball_savant_url(url: str) -> bool:
    """
    Check if URL is a Baseball Savant URL.
    
    Args:
        url: URL to check
        
    Returns:
        True if it's a Baseball Savant URL
    """
    return bool(url and 'baseballsavant.mlb.com' in url.lower())


def is_yahoo_fantasy_url(url: str) -> bool:
    """
    Check if URL is a Yahoo Fantasy URL.
    
    Args:
        url: URL to check
        
    Returns:
        True if it's a Yahoo Fantasy URL
    """
    return bool(url and 'fantasysports.yahoo.com' in url.lower())


def create_savant_link(name: str, mlbam_id: int) -> str:
    """
    Create Baseball Savant link using the official MLBAM ID.
    
    This is an alias for create_baseball_savant_url to match the original notebook function.
    
    Args:
        name: Player's full name
        mlbam_id: MLB Stats API player ID (MLBAM ID)
        
    Returns:
        Baseball Savant URL for the player
    """
    return create_baseball_savant_url(name, mlbam_id)


def create_yahoo_player_link(player_name: str) -> str:
    """
    Create Yahoo Fantasy player search link.
    
    Args:
        player_name: Player's full name
        
    Returns:
        Yahoo Fantasy player search URL
    """
    if not player_name:
        return ""
    
    import urllib.parse
    encoded_name = urllib.parse.quote_plus(player_name)
    return f"https://baseball.fantasysports.yahoo.com/b1/playersearch?search={encoded_name}"


def create_mlb_player_link(mlb_player_id: int) -> str:
    """
    Create MLB.com player link.
    
    This is an alias for create_mlb_player_url to match expected imports.
    
    Args:
        mlb_player_id: MLB Stats API player ID
        
    Returns:
        MLB.com player URL
    """
    return create_mlb_player_url(mlb_player_id)


def create_fangraphs_link(player_name: str) -> str:
    """
    Create FanGraphs player search link.
    
    This is an alias for create_fangraphs_url to match expected imports.
    
    Args:
        player_name: Player's full name
        
    Returns:
        FanGraphs search URL
    """
    return create_fangraphs_url(player_name)


def create_baseball_reference_link(player_name: str) -> str:
    """
    Create Baseball Reference player search link.
    
    Args:
        player_name: Player's full name
        
    Returns:
        Baseball Reference search URL
    """
    if not player_name:
        return ""
    
    import urllib.parse
    encoded_name = urllib.parse.quote_plus(player_name)
    return f"https://www.baseball-reference.com/search/search.fcgi?search={encoded_name}"


def create_rotowire_link(player_name: str) -> str:
    """
    Create RotoWire player search link.
    
    Args:
        player_name: Player's full name
        
    Returns:
        RotoWire search URL
    """
    if not player_name:
        return ""
    
    import urllib.parse
    encoded_name = urllib.parse.quote_plus(player_name)
    return f"https://www.rotowire.com/baseball/player.php?search={encoded_name}"


def create_espn_player_link(player_name: str) -> str:
    """
    Create ESPN player search link.
    
    Args:
        player_name: Player's full name
        
    Returns:
        ESPN search URL
    """
    if not player_name:
        return ""
    
    import urllib.parse
    encoded_name = urllib.parse.quote_plus(player_name)
    return f"https://www.espn.com/mlb/players/_/search/{encoded_name}"


def create_player_links_dict(player_name: str, mlb_player_id: int = None) -> dict:
    """
    Create a dictionary of player links for various sites.
    
    Args:
        player_name: Player's full name
        mlb_player_id: Optional MLB Stats API player ID
        
    Returns:
        Dictionary with site names as keys and URLs as values
    """
    links = {
        "Baseball Savant": create_savant_link(player_name, mlb_player_id) if mlb_player_id else "",
        "FanGraphs": create_fangraphs_link(player_name),
        "Baseball Reference": create_baseball_reference_link(player_name),
        "ESPN": create_espn_player_link(player_name),
        "RotoWire": create_rotowire_link(player_name),
        "Yahoo Fantasy": create_yahoo_player_link(player_name)
    }
    
    if mlb_player_id:
        links["MLB.com"] = create_mlb_player_link(mlb_player_id)
    
    return {k: v for k, v in links.items() if v}


def create_team_schedule_link(team_key: str) -> str:
    """
    Create Yahoo Fantasy team schedule link.
    
    Args:
        team_key: Yahoo Fantasy team key
        
    Returns:
        Yahoo Fantasy team schedule URL
    """
    if not team_key:
        return ""
    
    return f"https://baseball.fantasysports.yahoo.com/b1/{team_key}/schedule"


def create_league_standings_link(league_key: str) -> str:
    """
    Create Yahoo Fantasy league standings link.
    
    Args:
        league_key: Yahoo Fantasy league key
        
    Returns:
        Yahoo Fantasy league standings URL
    """
    if not league_key:
        return ""
    
    return f"https://baseball.fantasysports.yahoo.com/b1/{league_key}/standings"


def create_waiver_wire_link(league_key: str) -> str:
    """
    Create Yahoo Fantasy waiver wire link.
    
    Args:
        league_key: Yahoo Fantasy league key
        
    Returns:
        Yahoo Fantasy waiver wire URL
    """
    if not league_key:
        return ""
    
    return f"https://baseball.fantasysports.yahoo.com/b1/{league_key}/players?status=A&pos=ALL&cut_type=33&stat1=S_S_2024&myteam=0&sort=AR&sdir=1"


def shorten_url_display(url: str, max_length: int = 50) -> str:
    """
    Shorten URL for display purposes.
    
    Args:
        url: URL to shorten
        max_length: Maximum length for display
        
    Returns:
        Shortened URL string
    """
    if not url or len(url) <= max_length:
        return url
    
    return url[:max_length-3] + "..."