"""
Caching service for performance optimization.
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Callable, TypeVar, Union
import streamlit as st
import hashlib
import json
import pickle

from ..core.exceptions import CacheError
from ..core.constants import DEFAULT_CACHE_TTL_SECONDS, CACHE_KEYS

T = TypeVar('T')


class CacheService:
    """
    Multi-level caching service for the Yahoo Fantasy Baseball application.
    
    Provides:
    - Memory cache for fast access
    - Streamlit session state cache for user session persistence
    - Streamlit cache decorators for function-level caching
    - TTL (Time To Live) support
    - Cache statistics and management
    """
    
    def __init__(self, default_ttl: int = DEFAULT_CACHE_TTL_SECONDS) -> None:
        """
        Initialize cache service.
        
        Args:
            default_ttl: Default time-to-live in seconds
        """
        self.default_ttl = default_ttl
        self.logger = logging.getLogger(__name__)
        
        # Memory cache for fast access
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        
        # Initialize session state cache if not exists
        if 'cache_data' not in st.session_state:
            st.session_state.cache_data = {}
        
        # Cache statistics
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'clears': 0
        }
    
    def _generate_cache_key(self, key_template: str, **kwargs) -> str:
        """
        Generate cache key from template and parameters.
        
        Args:
            key_template: Cache key template from CACHE_KEYS
            **kwargs: Parameters to format into the template
            
        Returns:
            Formatted cache key
        """
        try:
            return key_template.format(**kwargs)
        except KeyError as e:
            raise CacheError(f"Missing parameter for cache key template: {e}")
    
    def _create_cache_entry(self, value: Any, ttl: Optional[int] = None) -> Dict[str, Any]:
        """Create cache entry with metadata."""
        return {
            'value': value,
            'timestamp': time.time(),
            'ttl': ttl or self.default_ttl,
            'expires_at': time.time() + (ttl or self.default_ttl)
        }
    
    def _is_expired(self, entry: Dict[str, Any]) -> bool:
        """Check if cache entry is expired."""
        return time.time() > entry.get('expires_at', 0)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from cache with multi-level lookup.
        
        Args:
            key: Cache key
            default: Default value if not found
            
        Returns:
            Cached value or default
        """
        try:
            # Check memory cache first
            if key in self._memory_cache:
                entry = self._memory_cache[key]
                if not self._is_expired(entry):
                    self._stats['hits'] += 1
                    self.logger.debug(f"Cache hit (memory): {key}")
                    return entry['value']
                else:
                    # Remove expired entry
                    del self._memory_cache[key]
            
            # Check session state cache
            if key in st.session_state.cache_data:
                entry = st.session_state.cache_data[key]
                if not self._is_expired(entry):
                    # Promote to memory cache
                    self._memory_cache[key] = entry
                    self._stats['hits'] += 1
                    self.logger.debug(f"Cache hit (session): {key}")
                    return entry['value']
                else:
                    # Remove expired entry
                    del st.session_state.cache_data[key]
            
            # Cache miss
            self._stats['misses'] += 1
            self.logger.debug(f"Cache miss: {key}")
            return default
            
        except Exception as e:
            self.logger.warning(f"Cache get error for key '{key}': {e}")
            return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set value in cache with TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (optional)
        """
        try:
            entry = self._create_cache_entry(value, ttl)
            
            # Store in both memory and session cache
            self._memory_cache[key] = entry
            st.session_state.cache_data[key] = entry
            
            self._stats['sets'] += 1
            self.logger.debug(f"Cache set: {key} (TTL: {entry['ttl']}s)")
            
        except Exception as e:
            self.logger.error(f"Cache set error for key '{key}': {e}")
            raise CacheError(f"Failed to set cache key '{key}': {str(e)}")
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if key was deleted
        """
        try:
            deleted = False
            
            if key in self._memory_cache:
                del self._memory_cache[key]
                deleted = True
            
            if key in st.session_state.cache_data:
                del st.session_state.cache_data[key]
                deleted = True
            
            if deleted:
                self._stats['deletes'] += 1
                self.logger.debug(f"Cache delete: {key}")
            
            return deleted
            
        except Exception as e:
            self.logger.error(f"Cache delete error for key '{key}': {e}")
            return False
    
    def clear(self, pattern: Optional[str] = None) -> int:
        """
        Clear cache entries, optionally matching a pattern.
        
        Args:
            pattern: Optional pattern to match keys (simple string contains)
            
        Returns:
            Number of entries cleared
        """
        try:
            cleared_count = 0
            
            # Clear memory cache
            if pattern:
                keys_to_delete = [k for k in self._memory_cache.keys() if pattern in k]
                for key in keys_to_delete:
                    del self._memory_cache[key]
                    cleared_count += 1
            else:
                cleared_count += len(self._memory_cache)
                self._memory_cache.clear()
            
            # Clear session cache
            if pattern:
                keys_to_delete = [k for k in st.session_state.cache_data.keys() if pattern in k]
                for key in keys_to_delete:
                    del st.session_state.cache_data[key]
            else:
                if hasattr(st.session_state, 'cache_data'):
                    cleared_count += len(st.session_state.cache_data)
                    st.session_state.cache_data.clear()
            
            self._stats['clears'] += 1
            self.logger.info(f"Cache cleared: {cleared_count} entries (pattern: {pattern})")
            
            return cleared_count
            
        except Exception as e:
            self.logger.error(f"Cache clear error: {e}")
            return 0
    
    def cleanup_expired(self) -> int:
        """
        Remove expired entries from cache.
        
        Returns:
            Number of expired entries removed
        """
        try:
            removed_count = 0
            current_time = time.time()
            
            # Clean memory cache
            expired_keys = [
                key for key, entry in self._memory_cache.items()
                if current_time > entry.get('expires_at', 0)
            ]
            for key in expired_keys:
                del self._memory_cache[key]
                removed_count += 1
            
            # Clean session cache
            expired_keys = [
                key for key, entry in st.session_state.cache_data.items()
                if current_time > entry.get('expires_at', 0)
            ]
            for key in expired_keys:
                del st.session_state.cache_data[key]
            
            if removed_count > 0:
                self.logger.info(f"Cleaned up {removed_count} expired cache entries")
            
            return removed_count
            
        except Exception as e:
            self.logger.error(f"Cache cleanup error: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self._stats['hits'] + self._stats['misses']
        hit_rate = (self._stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self._stats,
            'total_requests': total_requests,
            'hit_rate_percent': round(hit_rate, 2),
            'memory_cache_size': len(self._memory_cache),
            'session_cache_size': len(st.session_state.get('cache_data', {}))
        }
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get detailed cache information."""
        memory_keys = list(self._memory_cache.keys())
        session_keys = list(st.session_state.get('cache_data', {}).keys())
        
        return {
            'memory_cache_keys': memory_keys,
            'session_cache_keys': session_keys,
            'default_ttl': self.default_ttl,
            'stats': self.get_stats()
        }
    
    # Convenience methods for common cache patterns
    
    def get_team_schedule(self, team_id: int, start_date: str, end_date: str) -> Any:
        """Get cached team schedule."""
        key = self._generate_cache_key(
            CACHE_KEYS['TEAM_SCHEDULE'],
            team_id=team_id,
            start_date=start_date,
            end_date=end_date
        )
        return self.get(key)
    
    def set_team_schedule(self, team_id: int, start_date: str, end_date: str, 
                         schedule: Any, ttl: Optional[int] = None) -> None:
        """Cache team schedule."""
        key = self._generate_cache_key(
            CACHE_KEYS['TEAM_SCHEDULE'],
            team_id=team_id,
            start_date=start_date,
            end_date=end_date
        )
        self.set(key, schedule, ttl)
    
    def get_probable_starters(self, start_date: str, end_date: str) -> Any:
        """Get cached probable starters."""
        key = self._generate_cache_key(
            CACHE_KEYS['PROBABLE_STARTERS'],
            start_date=start_date,
            end_date=end_date
        )
        return self.get(key)
    
    def set_probable_starters(self, start_date: str, end_date: str, 
                            starters: Any, ttl: Optional[int] = None) -> None:
        """Cache probable starters."""
        key = self._generate_cache_key(
            CACHE_KEYS['PROBABLE_STARTERS'],
            start_date=start_date,
            end_date=end_date
        )
        self.set(key, starters, ttl)
    
    def get_waiver_players(self, league_id: str) -> Any:
        """Get cached waiver players."""
        key = self._generate_cache_key(
            CACHE_KEYS['WAIVER_PLAYERS'],
            league_id=league_id
        )
        return self.get(key)
    
    def set_waiver_players(self, league_id: str, players: Any, 
                          ttl: Optional[int] = None) -> None:
        """Cache waiver players."""
        key = self._generate_cache_key(
            CACHE_KEYS['WAIVER_PLAYERS'],
            league_id=league_id
        )
        self.set(key, players, ttl)
    
    def get_team_roster(self, team_key: str) -> Any:
        """Get cached team roster."""
        key = self._generate_cache_key(
            CACHE_KEYS['TEAM_ROSTER'],
            team_key=team_key
        )
        return self.get(key)
    
    def set_team_roster(self, team_key: str, roster: Any, 
                       ttl: Optional[int] = None) -> None:
        """Cache team roster."""
        key = self._generate_cache_key(
            CACHE_KEYS['TEAM_ROSTER'],
            team_key=team_key
        )
        self.set(key, roster, ttl)


# Streamlit cache decorators for function-level caching

def cache_data(ttl: int = DEFAULT_CACHE_TTL_SECONDS, show_spinner: bool = True):
    """
    Decorator for caching function results using Streamlit's cache_data.
    
    Args:
        ttl: Time-to-live in seconds
        show_spinner: Whether to show loading spinner
    """
    return st.cache_data(ttl=ttl, show_spinner=show_spinner)


def cache_resource(ttl: int = DEFAULT_CACHE_TTL_SECONDS, show_spinner: bool = True):
    """
    Decorator for caching resources using Streamlit's cache_resource.
    
    Args:
        ttl: Time-to-live in seconds
        show_spinner: Whether to show loading spinner
    """
    return st.cache_resource(ttl=ttl, show_spinner=show_spinner)


# Global cache service instance
_cache_service: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """
    Get the global cache service instance.
    
    Returns:
        CacheService instance
    """
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service


def clear_all_caches() -> Dict[str, int]:
    """
    Clear all application caches.
    
    Returns:
        Dictionary with clear results
    """
    results = {}
    
    # Clear service cache
    cache_service = get_cache_service()
    results['service_cache'] = cache_service.clear()
    
    # Clear Streamlit caches
    try:
        st.cache_data.clear()
        results['streamlit_data_cache'] = 'cleared'
    except Exception as e:
        results['streamlit_data_cache'] = f'error: {e}'
    
    try:
        st.cache_resource.clear()
        results['streamlit_resource_cache'] = 'cleared'
    except Exception as e:
        results['streamlit_resource_cache'] = f'error: {e}'
    
    return results