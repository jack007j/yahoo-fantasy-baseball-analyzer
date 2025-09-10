"""
MLB Player ID cache for faster lookups.

This module provides a pre-built cache of common MLB players and their IDs.
It can be used as a fallback when API lookups are slow or unavailable.
"""

import json
import os
from typing import Optional, Dict
from pathlib import Path

# Cache file location
CACHE_FILE = Path(__file__).parent / "mlb_player_ids.json"


def load_player_cache() -> Dict[str, int]:
    """Load the player ID cache from disk."""
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_player_cache(cache: Dict[str, int]) -> None:
    """Save the player ID cache to disk."""
    try:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache, f, indent=2)
    except Exception:
        pass


def get_cached_player_id(player_name: str) -> Optional[int]:
    """
    Get a player's MLB ID from the cache.
    
    Args:
        player_name: Player's full name
        
    Returns:
        MLB player ID if found in cache, None otherwise
    """
    cache = load_player_cache()
    return cache.get(player_name)


def update_player_cache(player_name: str, mlb_id: int) -> None:
    """
    Update the cache with a new player ID.
    
    Args:
        player_name: Player's full name
        mlb_id: MLB player ID
    """
    cache = load_player_cache()
    cache[player_name] = mlb_id
    save_player_cache(cache)


# Pre-populated cache of common 2024-2025 players
# This is a subset - the full cache would be built dynamically
FALLBACK_CACHE = {
    "Shohei Ohtani": 660271,
    "Ronald Acuna Jr.": 660670,
    "Mookie Betts": 605141,
    "Freddie Freeman": 518692,
    "Aaron Judge": 592450,
    "Juan Soto": 665742,
    "Mike Trout": 545361,
    "Gerrit Cole": 543037,
    "Spencer Strider": 675911,
    "Sandy Alcantara": 645261,
    "Jacob deGrom": 594798,
    "Shane Bieber": 669456,
    "Corbin Burnes": 669203,
    "Max Scherzer": 453286,
    "Clayton Kershaw": 477132,
    # Add more players as needed
}


def get_player_id_with_fallback(player_name: str) -> Optional[int]:
    """
    Get player ID from cache or fallback list.
    
    Args:
        player_name: Player's full name
        
    Returns:
        MLB player ID if found, None otherwise
    """
    # Try disk cache first
    mlb_id = get_cached_player_id(player_name)
    if mlb_id:
        return mlb_id
    
    # Try fallback cache
    return FALLBACK_CACHE.get(player_name)