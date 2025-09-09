"""
MLB Stats API client for retrieving baseball data.
"""

import logging
from datetime import date, datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd

from .base_client import BaseAPIClient
from ..core.constants import MLB_STATS_BASE_URL, MLB_SPORT_ID
from ..core.exceptions import MLBAPIError, DataValidationError
from ..models.team import MLBTeam


class MLBStatsClient(BaseAPIClient):
    """
    Client for MLB Stats API integration.
    
    Provides methods for:
    - Retrieving probable starting pitchers
    - Getting team schedules
    - Fetching player information
    - Team data and standings
    """
    
    def __init__(self) -> None:
        """Initialize MLB Stats API client."""
        super().__init__(
            base_url=MLB_STATS_BASE_URL,
            timeout=10,
            max_retries=3
        )
        self.logger = logging.getLogger(__name__)
        
        # Cache for team schedules (matches notebook implementation)
        self._team_schedule_cache: Dict[Tuple[int, str, str], List[date]] = {}
    
    def get_probable_starters(
        self, 
        start_date: date, 
        end_date: date
    ) -> Dict[int, Dict[str, Any]]:
        """
        Get confirmed probable starting pitchers for date range.
        
        This method replicates the notebook's logic for fetching probable starters
        from the MLB Stats API with hydrated pitcher and team information.
        
        Args:
            start_date: Start date for probable starters
            end_date: End date for probable starters
            
        Returns:
            Dictionary mapping MLB player IDs to pitcher information:
            {
                player_id: {
                    'name': str,
                    'date': date,
                    'team_id': int,
                    'team_name': str
                }
            }
            
        Raises:
            MLBAPIError: If API request fails
        """
        try:
            start_str = start_date.isoformat()
            end_str = end_date.isoformat()
            
            self.logger.info(f"Fetching probable starters from {start_str} to {end_str}")
            
            # Build API endpoint with hydration (matches notebook)
            endpoint = (
                f"schedule?sportId={MLB_SPORT_ID}"
                f"&startDate={start_str}"
                f"&endDate={end_str}"
                f"&hydrate=probablePitcher,team"
            )
            
            response_data = self.get(endpoint)
            
            confirmed_starters = {}
            
            if not response_data.get('dates'):
                self.logger.warning("No dates found in MLB API response")
                return confirmed_starters
            
            for day_data in response_data['dates']:
                game_date_str = day_data['date']
                game_date = datetime.strptime(game_date_str, '%Y-%m-%d').date()
                
                # Only include games within our target date range
                if not (start_date <= game_date <= end_date):
                    continue
                
                for game in day_data.get('games', []):
                    # Process both home and away probable pitchers
                    for team_key in ['home', 'away']:
                        team_data = game.get('teams', {}).get(team_key, {})
                        probable_pitcher = team_data.get('probablePitcher')
                        team_info = team_data.get('team')
                        
                        if (probable_pitcher and 
                            'id' in probable_pitcher and 
                            'fullName' in probable_pitcher and
                            team_info and 'id' in team_info):
                            
                            pitcher_id = probable_pitcher['id']
                            pitcher_name = probable_pitcher['fullName']
                            team_id = team_info['id']
                            team_name = team_info.get('name', 'Unknown Team')
                            
                            # Store pitcher info (avoid duplicates by using pitcher_id as key)
                            if pitcher_id not in confirmed_starters:
                                confirmed_starters[pitcher_id] = {
                                    'name': pitcher_name,
                                    'date': game_date,
                                    'team_id': team_id,
                                    'team_name': team_name
                                }
            
            self.logger.info(f"Found {len(confirmed_starters)} confirmed probable starters")
            return confirmed_starters
            
        except Exception as e:
            if isinstance(e, MLBAPIError):
                raise
            raise MLBAPIError(f"Failed to fetch probable starters: {str(e)}")
    
    def get_probable_pitchers(
        self,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """
        Alias for get_probable_starters that accepts string dates.
        
        Args:
            start_date: Start date string in ISO format (YYYY-MM-DD)
            end_date: End date string in ISO format (YYYY-MM-DD)
            
        Returns:
            Dictionary with 'dates' key containing schedule data
        """
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            # Get probable starters
            starters = self.get_probable_starters(start_date_obj, end_date_obj)
            
            # Convert to expected format for analysis service
            dates = []
            current_date = start_date_obj
            
            while current_date <= end_date_obj:
                date_games = []
                
                # Find all starters for this date
                for pitcher_id, starter_info in starters.items():
                    if starter_info['date'] == current_date:
                        # Create game structure expected by analysis service
                        game = {
                            'teams': {
                                'home': {
                                    'probablePitcher': {
                                        'id': pitcher_id,
                                        'fullName': starter_info['name']
                                    },
                                    'team': {
                                        'id': starter_info['team_id']
                                    }
                                }
                            }
                        }
                        date_games.append(game)
                
                if date_games:
                    dates.append({
                        'date': current_date.isoformat(),
                        'games': date_games
                    })
                
                current_date += timedelta(days=1)
            
            return {'dates': dates}
            
        except Exception as e:
            self.logger.error(f"Failed to get probable pitchers: {e}")
            return {'dates': []}
    
    def get_team_schedule(
        self, 
        team_id: int, 
        start_date: date, 
        end_date: date
    ) -> List[date]:
        """
        Get team schedule for date range with caching.
        
        This method replicates the notebook's team schedule caching logic.
        
        Args:
            team_id: MLB team ID
            start_date: Schedule start date
            end_date: Schedule end date
            
        Returns:
            List of game dates for the team
            
        Raises:
            MLBAPIError: If API request fails
        """
        # Check cache first (matches notebook implementation)
        start_str = start_date.isoformat()
        end_str = end_date.isoformat()
        cache_key = (team_id, start_str, end_str)
        
        if cache_key in self._team_schedule_cache:
            self.logger.debug(f"Using cached schedule for team {team_id}")
            return self._team_schedule_cache[cache_key]
        
        try:
            self.logger.debug(f"Fetching schedule for team {team_id} from {start_str} to {end_str}")
            
            endpoint = (
                f"schedule?sportId={MLB_SPORT_ID}"
                f"&teamId={team_id}"
                f"&startDate={start_str}"
                f"&endDate={end_str}"
            )
            
            response_data = self.get(endpoint)
            
            game_dates = []
            
            if response_data.get('dates'):
                for date_info in response_data['dates']:
                    game_date = datetime.strptime(date_info['date'], '%Y-%m-%d').date()
                    
                    # Check if there are actual games on this date
                    if (date_info.get('games') and 
                        any(g.get('gamePk') for g in date_info['games'])):
                        game_dates.append(game_date)
            
            # Sort dates and cache result
            game_dates.sort()
            self._team_schedule_cache[cache_key] = game_dates
            
            self.logger.debug(f"Found {len(game_dates)} games for team {team_id}")
            return game_dates
            
        except Exception as e:
            if isinstance(e, MLBAPIError):
                raise
            raise MLBAPIError(f"Failed to fetch team schedule for team {team_id}: {str(e)}")
    
    def check_potential_second_start(
        self, 
        team_id: int, 
        first_start_date: date, 
        fantasy_week_end_date: date
    ) -> bool:
        """
        Check if pitcher has potential for second start based on team schedule.
        
        This replicates the notebook's second start analysis logic.
        
        Args:
            team_id: MLB team ID
            first_start_date: Date of first confirmed start
            fantasy_week_end_date: End date of fantasy week
            
        Returns:
            True if pitcher likely has second start opportunity
        """
        if not team_id or pd.isna(team_id):
            return False
        
        try:
            team_id_int = int(team_id)
            
            # Look for games starting day after first start
            schedule_start_date = first_start_date + timedelta(days=1)
            # Look ahead beyond fantasy week for team's next 5 games
            schedule_end_date = fantasy_week_end_date + timedelta(days=5)
            
            game_dates = self.get_team_schedule(
                team_id_int, 
                schedule_start_date, 
                schedule_end_date
            )
            
            # If team has 5+ games, check if 5th game falls within fantasy week
            if len(game_dates) >= 5:
                potential_second_start_date = game_dates[4]  # 5th game (0-indexed)
                return potential_second_start_date <= fantasy_week_end_date
            
            return False
            
        except Exception as e:
            self.logger.warning(f"Error checking second start potential: {e}")
            return False
    
    def get_team_info(self, team_id: int) -> Optional[MLBTeam]:
        """
        Get detailed team information.
        
        Args:
            team_id: MLB team ID
            
        Returns:
            MLBTeam object or None if not found
        """
        try:
            endpoint = f"teams/{team_id}"
            response_data = self.get(endpoint)
            
            if not response_data.get('teams'):
                return None
            
            team_data = response_data['teams'][0]
            
            return MLBTeam(
                team_id=team_data['id'],
                name=team_data['name'],
                abbreviation=team_data.get('abbreviation'),
                division=team_data.get('division', {}).get('name'),
                league=team_data.get('league', {}).get('name')
            )
            
        except Exception as e:
            self.logger.warning(f"Failed to get team info for {team_id}: {e}")
            return None
    
    def get_all_teams(self) -> List[MLBTeam]:
        """
        Get all MLB teams.
        
        Returns:
            List of MLBTeam objects
        """
        try:
            endpoint = f"teams?sportId={MLB_SPORT_ID}"
            response_data = self.get(endpoint)
            
            teams = []
            for team_data in response_data.get('teams', []):
                team = MLBTeam(
                    team_id=team_data['id'],
                    name=team_data['name'],
                    abbreviation=team_data.get('abbreviation'),
                    division=team_data.get('division', {}).get('name'),
                    league=team_data.get('league', {}).get('name')
                )
                teams.append(team)
            
            return teams
            
        except Exception as e:
            self.logger.error(f"Failed to get all teams: {e}")
            return []
    
    def get_player_info(self, player_id: int) -> Optional[Dict[str, Any]]:
        """
        Get player information by MLB player ID.
        
        Args:
            player_id: MLB player ID
            
        Returns:
            Player information dictionary or None
        """
        try:
            endpoint = f"people/{player_id}"
            response_data = self.get(endpoint)
            
            if not response_data.get('people'):
                return None
            
            return response_data['people'][0]
            
        except Exception as e:
            self.logger.warning(f"Failed to get player info for {player_id}: {e}")
            return None
    
    def clear_cache(self) -> None:
        """Clear the team schedule cache."""
        self._team_schedule_cache.clear()
        self.logger.info("MLB client cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "cached_schedules": len(self._team_schedule_cache),
            "cache_keys": list(self._team_schedule_cache.keys())
        }