"""
Yahoo Fantasy API client with secure authentication.
"""

import logging
import time
from typing import Dict, List, Any, Optional
import pandas as pd
import yahoo_fantasy_api as yfa
from yahoo_oauth import OAuth2

from .base_client import BaseAPIClient
from ..core.config import get_config
from ..core.constants import YAHOO_FANTASY_BASE_URL, YAHOO_GAME_CODE
from ..core.exceptions import YahooAPIError, AuthenticationError, ConfigurationError
from ..models.player import Player
from ..models.team import FantasyTeam
from ..utils.text_utils import normalize_player_name


class YahooFantasyClient:
    """
    Client for Yahoo Fantasy API integration with secure authentication.
    
    This client handles:
    - Secure OAuth authentication using Streamlit secrets
    - League and team data retrieval
    - Player roster and waiver wire data
    - Automatic token refresh
    """
    
    def __init__(self) -> None:
        """Initialize Yahoo Fantasy API client with secure authentication."""
        self.logger = logging.getLogger(__name__)
        self._oauth_client: Optional[OAuth2] = None
        self._game: Optional[yfa.Game] = None
        self._is_configured = False
        self._configuration_error: Optional[str] = None
        self._initialize_oauth()
    
    def _initialize_oauth(self) -> None:
        """Initialize OAuth client using the original yahoo_oauth library."""
        try:
            # Try to load from file first (for local development)
            try:
                self._oauth_client = OAuth2(None, None, from_file='yahoo_oauth.json')
                self.logger.info("Loaded OAuth from yahoo_oauth.json file")
            except:
                # If file doesn't exist, try loading from Streamlit secrets (for deployment)
                import streamlit as st
                if hasattr(st, 'secrets') and 'yahoo_oauth' in st.secrets:
                    # Create a temporary JSON file from secrets
                    import json
                    import tempfile
                    import os

                    import time

                    # Set token as expired to force immediate refresh
                    # The tokens in secrets are static and always expired
                    oauth_data = {
                        'consumer_key': st.secrets['yahoo_oauth']['client_id'],
                        'consumer_secret': st.secrets['yahoo_oauth']['client_secret'],
                        'access_token': st.secrets['yahoo_oauth'].get('access_token', 'dummy_expired_token'),
                        'refresh_token': st.secrets['yahoo_oauth']['refresh_token'],
                        'token_time': time.time() - 7200,  # 2 hours ago - definitely expired
                        'token_type': 'bearer',
                        'expires_in': 3600,  # Valid for 1 hour
                        'guid': None
                    }

                    # Write to temp file
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                        json.dump(oauth_data, f)
                        temp_file = f.name

                    try:
                        self._oauth_client = OAuth2(None, None, from_file=temp_file)
                        self.logger.info("Loaded OAuth from Streamlit secrets")
                    finally:
                        # Clean up temp file
                        if os.path.exists(temp_file):
                            os.remove(temp_file)
                else:
                    raise Exception("No OAuth configuration found (neither file nor secrets)")

            # Always check and refresh token if needed
            try:
                if not self._oauth_client.token_is_valid():
                    self.logger.info("Token expired, refreshing...")
                    self._oauth_client.refresh_access_token()
                    self.logger.info("Token refreshed successfully")
                else:
                    # Double-check by trying to refresh anyway if we're using secrets
                    # (since the token from secrets is always expired)
                    import streamlit as st
                    if hasattr(st, 'secrets') and 'yahoo_oauth' in st.secrets:
                        self.logger.info("Using Streamlit secrets - forcing token refresh...")
                        self._oauth_client.refresh_access_token()
                        self.logger.info("Token refreshed successfully")
                    else:
                        self.logger.info("Token is valid, no refresh needed")
            except Exception as refresh_error:
                self.logger.error(f"Token refresh failed: {refresh_error}")
                raise AuthenticationError(f"Failed to refresh OAuth token: {str(refresh_error)}")

            # Initialize game object with the OAuth client
            self._game = yfa.Game(self._oauth_client, YAHOO_GAME_CODE)
            self._is_configured = True

            self.logger.info("Yahoo Fantasy API client initialized successfully with yahoo_oauth")

        except Exception as e:
            self._configuration_error = f"Failed to initialize Yahoo OAuth: {str(e)}"
            self.logger.warning(self._configuration_error)
            self._is_configured = False
    
    def is_configured(self) -> bool:
        """Check if Yahoo OAuth is properly configured."""
        return self._is_configured
    
    def get_configuration_error(self) -> Optional[str]:
        """Get configuration error message if any."""
        return self._configuration_error
    
    def _ensure_authenticated(self) -> None:
        """Ensure OAuth token is valid, refresh if necessary."""
        if not self._is_configured:
            raise AuthenticationError(
                self._configuration_error or "Yahoo OAuth not configured"
            )
        
        if not self._oauth_client:
            raise AuthenticationError("OAuth client not initialized")
        
        if not self._oauth_client.token_is_valid():
            try:
                self.logger.info("Refreshing expired OAuth token")
                self._oauth_client.refresh_access_token()
            except Exception as e:
                raise AuthenticationError(f"Failed to refresh OAuth token: {str(e)}")
    
    def get_league(self, league_id: str) -> Optional[yfa.League]:
        """
        Get Yahoo Fantasy league object.

        Args:
            league_id: Yahoo Fantasy league ID (e.g., "458.l.135626")

        Returns:
            Yahoo Fantasy League object or None if not found

        Raises:
            YahooAPIError: If league retrieval fails
        """
        try:
            self._ensure_authenticated()

            if not self._game:
                raise YahooAPIError("Game object not initialized")

            # Get available league IDs for current year
            from datetime import date
            current_year = date.today().year

            try:
                league_ids = self._game.league_ids(year=current_year)
            except Exception as league_error:
                # Log the full error for debugging
                self.logger.error(f"Failed to get league IDs: {league_error}")
                # Try to extract more info from the error
                if hasattr(league_error, 'response'):
                    self.logger.error(f"Response content: {getattr(league_error.response, 'content', 'N/A')}")
                raise YahooAPIError(f"Failed to get league IDs: {str(league_error)[:200]}")

            if league_id not in league_ids:
                available_leagues = ", ".join(league_ids) if league_ids else "None"
                raise YahooAPIError(
                    f"League ID {league_id} not found for {current_year}. "
                    f"Available leagues: {available_leagues}"
                )

            league = self._game.to_league(league_id)
            self.logger.info(f"Successfully retrieved league {league_id}")
            return league

        except Exception as e:
            if isinstance(e, (YahooAPIError, AuthenticationError)):
                raise
            # Include more error details
            error_msg = str(e)
            if hasattr(e, '__dict__'):
                error_msg += f" | Details: {e.__dict__}"
            raise YahooAPIError(f"Failed to get league {league_id}: {error_msg[:500]}")

    def get_league_teams(self, league_id: str) -> Dict[str, str]:
        """
        Get all teams in a league with their names and team keys.

        Args:
            league_id: Yahoo Fantasy league ID (e.g., "458.l.135626")

        Returns:
            Dictionary mapping team keys to team names

        Raises:
            YahooAPIError: If teams retrieval fails
        """
        try:
            self._ensure_authenticated()

            league = self.get_league(league_id)
            if not league:
                raise YahooAPIError(f"Could not retrieve league {league_id}")

            teams_data = league.teams()
            teams_dict = {}

            for team_key, team_info in teams_data.items():
                # Extract team name
                team_name = team_info.get('name', f"Team {team_key}")
                teams_dict[team_key] = team_name
                self.logger.debug(f"Found team: {team_name} ({team_key})")

            self.logger.info(f"Retrieved {len(teams_dict)} teams from league {league_id}")
            return teams_dict

        except Exception as e:
            if isinstance(e, (YahooAPIError, AuthenticationError)):
                raise
            raise YahooAPIError(f"Failed to get teams for league {league_id}: {str(e)}")
    
    def get_waiver_pitchers(self, league: yfa.League) -> List[Player]:
        """
        Get pitchers available on waiver wire.
        
        This method replicates the notebook's waiver pitcher retrieval logic.
        
        Args:
            league: Yahoo Fantasy League object
            
        Returns:
            List of Player objects for pitchers on waivers
            
        Raises:
            YahooAPIError: If waiver data retrieval fails
        """
        try:
            self.logger.info("Fetching waiver players...")
            
            waiver_players = league.waivers()
            
            if not waiver_players:
                self.logger.warning("No players found on waivers")
                return []
            
            # Convert to DataFrame for processing (matches notebook)
            df = pd.DataFrame(waiver_players)
            self.logger.info(f"Retrieved {len(df)} players from waivers")
            
            # Filter for pitchers
            pitchers_df = df[df['eligible_positions'].apply(
                lambda x: any(pos in ['SP', 'RP'] for pos in x)
            )]
            
            self.logger.info(f"Found {len(pitchers_df)} pitchers on waivers")
            
            # Convert to Player objects
            pitchers = []
            for _, row in pitchers_df.iterrows():
                try:
                    player = Player(
                        name=row['name'],
                        yahoo_player_id=row.get('player_id'),
                        eligible_positions=row.get('eligible_positions', []),
                        percent_owned=float(row.get('percent_owned', 0)),
                        source="Waiver"
                    )
                    pitchers.append(player)
                except Exception as e:
                    self.logger.warning(f"Failed to create Player object for {row.get('name', 'Unknown')}: {e}")
                    continue
            
            return pitchers
            
        except Exception as e:
            if isinstance(e, YahooAPIError):
                raise
            raise YahooAPIError(f"Failed to fetch waiver pitchers: {str(e)}")
    
    def get_team_pitchers(self, league: yfa.League, team_key: str) -> List[Player]:
        """
        Get pitchers from a specific fantasy team roster.
        
        This method replicates the notebook's team roster retrieval logic.
        
        Args:
            league: Yahoo Fantasy League object
            team_key: Yahoo Fantasy team key (e.g., "458.l.135626.t.6")
            
        Returns:
            List of Player objects for pitchers on the team
            
        Raises:
            YahooAPIError: If team data retrieval fails
        """
        try:
            self.logger.info(f"Fetching pitchers for team key: {team_key}")
            
            # Get all teams to find the target team
            all_teams_dict = league.teams()
            
            my_team_info = None
            for team_id, team_data in all_teams_dict.items():
                if team_data.get('team_key') == team_key:
                    my_team_info = team_data
                    break
            
            if not my_team_info:
                raise YahooAPIError(f"Could not find team with key '{team_key}'")
            
            team_name = my_team_info.get('name', f"Team Key {team_key}")
            self.logger.info(f"Found team '{team_name}'")
            
            # Get team roster
            team_obj = yfa.Team(league.sc, team_key)
            from datetime import date
            roster = team_obj.roster(day=date.today())
            
            if not roster:
                self.logger.warning(f"No players found on roster for {team_name}")
                return []
            
            # Convert to DataFrame and filter for pitchers
            df = pd.DataFrame(roster)
            pitchers_df = df[df['eligible_positions'].apply(
                lambda x: any(pos in ['SP', 'RP'] for pos in x)
            )]
            
            self.logger.info(f"Found {len(pitchers_df)} pitchers on team '{team_name}'")
            
            # Convert to Player objects
            pitchers = []
            for _, row in pitchers_df.iterrows():
                try:
                    player = Player(
                        name=row['name'],
                        yahoo_player_id=row.get('player_id'),
                        eligible_positions=row.get('eligible_positions', []),
                        percent_owned=float(row.get('percent_owned', 0)),
                        source="My Team"
                    )
                    pitchers.append(player)
                except Exception as e:
                    self.logger.warning(f"Failed to create Player object for {row.get('name', 'Unknown')}: {e}")
                    continue
            
            return pitchers
            
        except Exception as e:
            if isinstance(e, YahooAPIError):
                raise
            raise YahooAPIError(f"Failed to fetch team pitchers for '{team_key}': {str(e)}")
    
    def get_combined_pitchers(self, league_id: str, team_key: str) -> List[Player]:
        """
        Get combined list of pitchers from team roster and waiver wire.
        
        Args:
            league_id: Yahoo Fantasy league ID
            team_key: Yahoo Fantasy team key
            
        Returns:
            Combined list of Player objects from team and waivers
        """
        try:
            league = self.get_league(league_id)
            if not league:
                raise YahooAPIError(f"Could not retrieve league {league_id}")
            
            # Get waiver pitchers
            waiver_pitchers = self.get_waiver_pitchers(league)
            
            # Get team pitchers
            team_pitchers = self.get_team_pitchers(league, team_key)
            
            # Combine lists
            all_pitchers = team_pitchers + waiver_pitchers
            
            self.logger.info(
                f"Combined pitchers: {len(team_pitchers)} from team, "
                f"{len(waiver_pitchers)} from waivers, "
                f"{len(all_pitchers)} total"
            )
            
            return all_pitchers
            
        except Exception as e:
            if isinstance(e, YahooAPIError):
                raise
            raise YahooAPIError(f"Failed to get combined pitchers: {str(e)}")
    
    def get_team_info(self, league_id: str, team_key: str) -> Optional[FantasyTeam]:
        """
        Get detailed fantasy team information.
        
        Args:
            league_id: Yahoo Fantasy league ID
            team_key: Yahoo Fantasy team key
            
        Returns:
            FantasyTeam object or None if not found
        """
        try:
            league = self.get_league(league_id)
            if not league:
                return None
            
            all_teams = league.teams()
            
            for team_id, team_data in all_teams.items():
                if team_data.get('team_key') == team_key:
                    return FantasyTeam(
                        team_key=team_key,
                        team_id=team_id,
                        name=team_data.get('name', 'Unknown Team'),
                        league_id=league_id,
                        manager_name=team_data.get('manager', {}).get('nickname'),
                        wins=int(team_data.get('team_standings', {}).get('outcome_totals', {}).get('wins', 0)),
                        losses=int(team_data.get('team_standings', {}).get('outcome_totals', {}).get('losses', 0)),
                        ties=int(team_data.get('team_standings', {}).get('outcome_totals', {}).get('ties', 0)),
                        rank=int(team_data.get('team_standings', {}).get('rank', 0))
                    )
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Failed to get team info: {e}")
            return None
    
    def get_team_roster(self, team_key: str) -> List[Dict[str, Any]]:
        """
        Get all players from a specific fantasy team roster.
        
        Args:
            team_key: Yahoo Fantasy team key (e.g., "458.l.135626.t.6")
            
        Returns:
            List of player dictionaries for all players on the team
            
        Raises:
            YahooAPIError: If team data retrieval fails
        """
        try:
            self.logger.info(f"Fetching roster for team key: {team_key}")
            
            # Extract league_id from team_key (format: "game.l.league_id.t.team_id")
            parts = team_key.split('.')
            if len(parts) < 4:
                raise YahooAPIError(f"Invalid team key format: {team_key}")
            
            league_id = f"{parts[0]}.l.{parts[2]}"
            league = self.get_league(league_id)
            if not league:
                raise YahooAPIError(f"Could not retrieve league {league_id}")
            
            # Get all teams to find the target team
            all_teams_dict = league.teams()
            
            my_team_info = None
            for team_id, team_data in all_teams_dict.items():
                if team_data.get('team_key') == team_key:
                    my_team_info = team_data
                    break
            
            if not my_team_info:
                raise YahooAPIError(f"Could not find team with key '{team_key}'")
            
            team_name = my_team_info.get('name', f"Team Key {team_key}")
            self.logger.info(f"Found team '{team_name}'")
            
            # Get team roster
            team_obj = yfa.Team(league.sc, team_key)
            from datetime import date
            roster = team_obj.roster(day=date.today())
            
            if not roster:
                self.logger.warning(f"No players found on roster for {team_name}")
                return []
            
            self.logger.info(f"Found {len(roster)} players on team '{team_name}'")
            
            # Return the raw roster data as dictionaries
            return roster
            
        except Exception as e:
            if isinstance(e, YahooAPIError):
                raise
            raise YahooAPIError(f"Failed to fetch team roster for '{team_key}': {str(e)}")
    
    def get_waiver_players(self, league_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all players available on waiver wire.
        
        Args:
            league_id: Optional league ID. If not provided, will try to get from available leagues.
            
        Returns:
            List of player dictionaries from waiver wire
            
        Raises:
            YahooAPIError: If waiver data retrieval fails
        """
        try:
            # If no league_id provided, try to get the first available league
            if not league_id:
                available_leagues = self.get_available_leagues()
                if not available_leagues:
                    raise YahooAPIError("No leagues available for current user")
                league_id = available_leagues[0]
            
            league = self.get_league(league_id)
            if not league:
                raise YahooAPIError(f"Could not retrieve league {league_id}")
            
            self.logger.info("Fetching waiver players...")
            
            waiver_players = league.waivers()
            
            if not waiver_players:
                self.logger.warning("No players found on waivers")
                return []
            
            self.logger.info(f"Retrieved {len(waiver_players)} players from waivers")
            return waiver_players
            
        except Exception as e:
            if isinstance(e, YahooAPIError):
                raise
            raise YahooAPIError(f"Failed to fetch waiver players: {str(e)}")
    
    def validate_league_access(self, league_id: str) -> bool:
        """
        Validate that the user has access to the specified league.
        
        Args:
            league_id: Yahoo Fantasy league ID to validate
            
        Returns:
            True if user has access to the league
        """
        try:
            league = self.get_league(league_id)
            return league is not None
        except Exception:
            return False
    
    def get_available_leagues(self) -> List[str]:
        """
        Get list of available league IDs for the current user.
        
        Returns:
            List of league ID strings
        """
        try:
            self._ensure_authenticated()
            
            if not self._game:
                return []
            
            from datetime import date
            current_year = date.today().year
            return self._game.league_ids(year=current_year)
            
        except Exception as e:
            self.logger.warning(f"Failed to get available leagues: {e}")
            return []