"""
Analysis service for Yahoo Fantasy Baseball application.

This service orchestrates the analysis workflow, combining data from Yahoo Fantasy API
and MLB Stats API to identify optimal Monday/Tuesday starting pitchers.
"""

import time
import unicodedata
import re
from datetime import date, timedelta, datetime
from typing import List, Optional, Dict, Any, Tuple
import pandas as pd
import streamlit as st

from ..models.player import Player
from ..models.analysis import PitcherAnalysis, FantasyWeek
from ..models.team import FantasyTeam, MLBTeam
from ..api.yahoo_client import YahooFantasyClient
from ..api.mlb_client import MLBStatsClient
from ..api.mlb_player_lookup import search_mlb_player
from ..data.mlb_player_cache import get_player_id_with_fallback, update_player_cache
from ..core.exceptions import AnalysisError, APIError
from ..utils.text_utils import slugify
from ..utils.url_utils import create_baseball_savant_url
from .cache_service import CacheService


class AnalysisService:
    """
    Service class for performing fantasy baseball analysis.
    
    This service combines data from Yahoo Fantasy API and MLB Stats API to:
    - Find confirmed probable starters for Monday/Tuesday
    - Identify potential second starts
    - Compare waiver wire vs. roster options
    - Generate Baseball Savant links
    """
    
    def __init__(self, yahoo_client: YahooFantasyClient, mlb_client: MLBStatsClient, cache_service: CacheService):
        """Initialize the analysis service."""
        self.yahoo_client = yahoo_client
        self.mlb_client = mlb_client
        self.cache_service = cache_service
        
    def analyze_next_fantasy_week(self, team_key: str) -> Tuple[FantasyWeek, List[PitcherAnalysis]]:
        """
        Perform complete analysis for the next fantasy week.
        
        Args:
            team_key: Yahoo Fantasy team key (e.g., '458.l.135626.t.6')
            
        Returns:
            Tuple of (FantasyWeek, List[PitcherAnalysis])
            
        Raises:
            AnalysisError: If analysis fails
        """
        start_time = time.time()
        
        try:
            # Calculate next fantasy week dates
            fantasy_week = self._calculate_next_fantasy_week()
            
            # Get pitcher data from Yahoo
            waiver_pitchers = self._get_waiver_pitchers()
            my_team_pitchers = self._get_my_team_pitchers(team_key)
            
            # Combine all pitchers
            all_pitchers = self._combine_pitcher_data(waiver_pitchers, my_team_pitchers)
            
            # Get confirmed probable starters from MLB API
            confirmed_starters = self._get_confirmed_probable_starters(fantasy_week)
            
            # Match and analyze pitchers
            pitcher_analyses = self._analyze_matched_pitchers(
                all_pitchers, confirmed_starters, fantasy_week
            )
            
            # Update fantasy week with results
            fantasy_week.total_pitchers_analyzed = len(pitcher_analyses)
            fantasy_week.my_team_pitchers = len([p for p in pitcher_analyses if p.player.source == "My Team"])
            fantasy_week.waiver_pitchers = len([p for p in pitcher_analyses if p.player.source == "Waiver"])
            fantasy_week.analysis_completed = True
            fantasy_week.analysis_duration = time.time() - start_time
            
            return fantasy_week, pitcher_analyses
            
        except Exception as e:
            raise AnalysisError(f"Analysis failed: {str(e)}") from e
    
    def get_team_roster(self, team_key: str) -> List[Player]:
        """
        Get complete team roster for display.
        
        Args:
            team_key: Yahoo Fantasy team key
            
        Returns:
            List of Player objects representing the team roster
        """
        try:
            roster_data = self.yahoo_client.get_team_roster(team_key)
            players = []
            
            for player_data in roster_data:
                player = Player(
                    name=player_data.get('name', ''),
                    yahoo_player_id=player_data.get('player_id'),
                    eligible_positions=player_data.get('eligible_positions', []),
                    percent_owned=player_data.get('percent_owned', 0.0),
                    mlb_team_name=player_data.get('editorial_team_full_name', ''),
                    source="My Team"
                )
                
                # Try to find MLB player ID - first from cache, then API
                mlb_id = get_player_id_with_fallback(player.name)
                if not mlb_id:
                    mlb_id = search_mlb_player(player.name)
                    if mlb_id:
                        # Cache it for next time
                        update_player_cache(player.name, mlb_id)
                
                if mlb_id:
                    player.mlb_player_id = mlb_id
                    player.baseball_savant_url = create_baseball_savant_url(
                        player.name, mlb_id
                    )
                
                players.append(player)
            
            return players
            
        except Exception as e:
            raise AnalysisError(f"Failed to get team roster: {str(e)}") from e
    
    def _calculate_next_fantasy_week(self) -> FantasyWeek:
        """Calculate the next fantasy week dates."""
        today = date.today()
        days_until_next_monday = (7 - today.weekday()) % 7
        if days_until_next_monday == 0:
            days_until_next_monday = 7
            
        start_date = today + timedelta(days=days_until_next_monday)
        end_date = start_date + timedelta(days=6)
        
        # Calculate week number (approximate)
        week_number = start_date.isocalendar()[1]
        
        return FantasyWeek(
            start_date=start_date,
            end_date=end_date,
            week_number=week_number,
            target_days=["Monday", "Tuesday"]
        )
    
    def _get_waiver_pitchers(self) -> List[Player]:
        """Get pitcher data from waiver wire."""
        try:
            waiver_data = self.yahoo_client.get_waiver_players()
            pitchers = []
            
            for player_data in waiver_data:
                if self._is_pitcher(player_data.get('eligible_positions', [])):
                    player = Player(
                        name=player_data.get('name', ''),
                        yahoo_player_id=player_data.get('player_id'),
                        eligible_positions=player_data.get('eligible_positions', []),
                        percent_owned=player_data.get('percent_owned', 0.0),
                        mlb_team_name=player_data.get('editorial_team_full_name', ''),
                        source="Waiver"
                    )
                    pitchers.append(player)
            
            return pitchers
            
        except Exception as e:
            st.warning(f"Could not fetch waiver pitchers: {str(e)}")
            return []
    
    def _get_my_team_pitchers(self, team_key: str) -> List[Player]:
        """Get pitcher data from user's team."""
        try:
            roster_data = self.yahoo_client.get_team_roster(team_key)
            pitchers = []
            
            for player_data in roster_data:
                if self._is_pitcher(player_data.get('eligible_positions', [])):
                    player = Player(
                        name=player_data.get('name', ''),
                        yahoo_player_id=player_data.get('player_id'),
                        eligible_positions=player_data.get('eligible_positions', []),
                        percent_owned=player_data.get('percent_owned', 0.0),
                        mlb_team_name=player_data.get('editorial_team_full_name', ''),
                        source="My Team"
                    )
                    pitchers.append(player)
            
            return pitchers
            
        except Exception as e:
            st.warning(f"Could not fetch team roster: {str(e)}")
            return []
    
    def _is_pitcher(self, positions: List[str]) -> bool:
        """Check if player is a pitcher based on eligible positions."""
        pitcher_positions = {'SP', 'RP', 'P'}
        return any(pos in pitcher_positions for pos in positions)
    
    def _combine_pitcher_data(self, waiver_pitchers: List[Player], my_team_pitchers: List[Player]) -> List[Player]:
        """Combine waiver and team pitcher data."""
        all_pitchers = []
        all_pitchers.extend(waiver_pitchers)
        all_pitchers.extend(my_team_pitchers)
        return all_pitchers
    
    def _get_confirmed_probable_starters(self, fantasy_week: FantasyWeek) -> Dict[int, Dict[str, Any]]:
        """Get confirmed probable starters from MLB API."""
        try:
            start_date_str = fantasy_week.start_date.isoformat()
            end_date_str = (fantasy_week.start_date + timedelta(days=10)).isoformat()
            
            schedule_data = self.mlb_client.get_probable_pitchers(start_date_str, end_date_str)
            confirmed_starters = {}
            
            if schedule_data and schedule_data.get('dates'):
                for day in schedule_data['dates']:
                    game_date = datetime.strptime(day['date'], '%Y-%m-%d').date()
                    
                    if fantasy_week.start_date <= game_date <= fantasy_week.end_date:
                        for game in day.get('games', []):
                            for team_key in ['home', 'away']:
                                probable = game.get('teams', {}).get(team_key, {}).get('probablePitcher')
                                team_info = game.get('teams', {}).get(team_key, {}).get('team')
                                
                                if (probable and 'id' in probable and 'fullName' in probable 
                                    and team_info and 'id' in team_info):
                                    
                                    pid = probable['id']
                                    pname = probable['fullName']
                                    tid = team_info['id']
                                    
                                    if pid not in confirmed_starters:
                                        confirmed_starters[pid] = {
                                            'name': pname,
                                            'date': game_date,
                                            'team_id': tid
                                        }
            
            return confirmed_starters
            
        except Exception as e:
            st.warning(f"Could not fetch probable starters: {str(e)}")
            return {}
    
    def _analyze_matched_pitchers(
        self, 
        all_pitchers: List[Player], 
        confirmed_starters: Dict[int, Dict[str, Any]], 
        fantasy_week: FantasyWeek
    ) -> List[PitcherAnalysis]:
        """Match confirmed starters with Yahoo data and analyze."""
        pitcher_analyses = []
        
        # Get Monday and Tuesday dates
        monday_date = fantasy_week.start_date
        tuesday_date = fantasy_week.start_date + timedelta(days=1)
        
        for mlb_api_id, starter_info in confirmed_starters.items():
            # Filter for Monday/Tuesday starts only
            if starter_info['date'] in [monday_date, tuesday_date]:
                # Try to match by name
                matched_player = self._find_matching_player(all_pitchers, starter_info['name'])
                
                if matched_player:
                    # Check for potential second start
                    potential_second = self._check_potential_second_start(
                        starter_info['team_id'], 
                        starter_info['date'], 
                        fantasy_week.end_date
                    )
                    
                    # Create Baseball Savant URL
                    matched_player.mlb_player_id = mlb_api_id
                    matched_player.baseball_savant_url = create_baseball_savant_url(
                        starter_info['name'], mlb_api_id
                    )
                    matched_player.confirmed_start_date = starter_info['date']
                    matched_player.potential_second_start = potential_second
                    
                    # Create analysis
                    analysis = PitcherAnalysis(
                        player=matched_player,
                        confirmed_start_date=starter_info['date'],
                        is_monday_tuesday_start=True,
                        potential_second_start=potential_second,
                        second_start_likelihood=0.8 if potential_second else 0.0,
                        recommendation_score=self._calculate_recommendation_score(matched_player, potential_second),
                        recommendation_reason=self._generate_recommendation_reason(matched_player, potential_second)
                    )
                    
                    pitcher_analyses.append(analysis)
        
        # Sort by priority score
        pitcher_analyses.sort(key=lambda x: x.priority_score, reverse=True)
        return pitcher_analyses
    
    def _find_matching_player(self, all_pitchers: List[Player], mlb_name: str) -> Optional[Player]:
        """Find matching player by name."""
        normalized_mlb_name = slugify(mlb_name)
        
        for player in all_pitchers:
            if slugify(player.name) == normalized_mlb_name:
                return player
        
        return None
    
    def _check_potential_second_start(self, team_id: int, first_start_date: date, fantasy_week_end: date) -> bool:
        """Check if pitcher has potential for second start based on team schedule."""
        try:
            schedule_start = first_start_date + timedelta(days=1)
            schedule_end = fantasy_week_end + timedelta(days=5)
            
            game_dates = self.mlb_client.get_team_schedule(
                team_id, 
                schedule_start.isoformat(), 
                schedule_end.isoformat()
            )
            
            if len(game_dates) >= 5:
                potential_second_start_date = game_dates[4]
                return potential_second_start_date <= fantasy_week_end
            
            return False
            
        except Exception:
            return False
    
    def _calculate_recommendation_score(self, player: Player, potential_second: bool) -> float:
        """Calculate recommendation score for a player."""
        score = 0.0
        
        # Base score from ownership percentage
        score += player.percent_owned / 100.0
        
        # Bonus for my team players
        if player.source == "My Team":
            score += 2.0
        
        # Bonus for potential second start
        if potential_second:
            score += 1.5
        
        return score
    
    def _generate_recommendation_reason(self, player: Player, potential_second: bool) -> str:
        """Generate recommendation reason text."""
        reasons = []
        
        if player.source == "My Team":
            reasons.append("Already on your team")
        
        if potential_second:
            reasons.append("Likely second start")
        
        if player.percent_owned < 50:
            reasons.append("Low ownership")
        elif player.percent_owned > 80:
            reasons.append("High ownership")
        
        return "; ".join(reasons) if reasons else "Confirmed Monday/Tuesday start"