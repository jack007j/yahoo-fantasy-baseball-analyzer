"""
MLB Player lookup service for finding player IDs by name.

This module provides functionality to search for MLB players and get their IDs
for use in generating Baseball Savant links and profile images.
"""

import requests
import logging
from typing import Optional, Dict, Any, List
from functools import lru_cache
import unicodedata
import re

logger = logging.getLogger(__name__)


def normalize_name(name: str) -> str:
    """Normalize a player name for matching."""
    if not name:
        return ""
    # Remove accents
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')
    # Convert to lowercase and remove non-alphanumeric
    name = re.sub(r'[^a-z0-9\s]', '', name.lower())
    # Remove extra spaces
    name = ' '.join(name.split())
    return name


@lru_cache(maxsize=500)
def search_mlb_player(player_name: str) -> Optional[int]:
    """
    Search for an MLB player by name and return their MLB ID.
    
    Args:
        player_name: Player's full name
        
    Returns:
        MLB player ID if found, None otherwise
    """
    if not player_name:
        return None
    
    try:
        # Use MLB Stats API search endpoint
        search_url = f"https://statsapi.mlb.com/api/v1/people/search?names={player_name}&sportIds=1&active=true"
        response = requests.get(search_url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data.get('people'):
            normalized_search = normalize_name(player_name)
            
            # Try exact match first
            for player in data['people']:
                if normalize_name(player.get('fullName', '')) == normalized_search:
                    return player.get('id')
            
            # If no exact match, return first result (usually best match)
            if data['people']:
                return data['people'][0].get('id')
        
        return None
        
    except Exception as e:
        logger.warning(f"Failed to search for player {player_name}: {e}")
        return None


@lru_cache(maxsize=500)
def get_player_info(player_name: str) -> Optional[Dict[str, Any]]:
    """
    Get full player information including MLB ID and current team.
    
    Args:
        player_name: Player's full name
        
    Returns:
        Dict with player info including 'id', 'fullName', 'currentTeam' if found
    """
    if not player_name:
        return None
    
    try:
        # Search for the player
        search_url = f"https://statsapi.mlb.com/api/v1/people/search?names={player_name}&sportIds=1&active=true"
        response = requests.get(search_url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data.get('people'):
            normalized_search = normalize_name(player_name)
            
            # Try exact match first
            for player in data['people']:
                if normalize_name(player.get('fullName', '')) == normalized_search:
                    player_id = player.get('id')
                    if player_id:
                        # Get detailed info
                        detail_url = f"https://statsapi.mlb.com/api/v1/people/{player_id}?hydrate=currentTeam"
                        detail_response = requests.get(detail_url, timeout=5)
                        detail_response.raise_for_status()
                        detail_data = detail_response.json()
                        
                        if detail_data.get('people'):
                            return detail_data['people'][0]
                    return player
            
            # If no exact match, use first result
            if data['people']:
                player = data['people'][0]
                player_id = player.get('id')
                if player_id:
                    # Get detailed info
                    detail_url = f"https://statsapi.mlb.com/api/v1/people/{player_id}?hydrate=currentTeam"
                    detail_response = requests.get(detail_url, timeout=5)
                    detail_response.raise_for_status()
                    detail_data = detail_response.json()
                    
                    if detail_data.get('people'):
                        return detail_data['people'][0]
                return player
        
        return None
        
    except Exception as e:
        logger.warning(f"Failed to get info for player {player_name}: {e}")
        return None


def batch_search_players(player_names: List[str]) -> Dict[str, Optional[int]]:
    """
    Search for multiple players and return a mapping of names to MLB IDs.
    
    Args:
        player_names: List of player names to search
        
    Returns:
        Dict mapping player names to MLB IDs (or None if not found)
    """
    results = {}
    for name in player_names:
        results[name] = search_mlb_player(name)
    return results