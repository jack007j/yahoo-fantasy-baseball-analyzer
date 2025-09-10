"""
Player data model for Yahoo Fantasy Baseball application.
"""

from datetime import date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class Player(BaseModel):
    """
    Represents a baseball player with fantasy-relevant information.
    
    This model combines data from both Yahoo Fantasy API and MLB Stats API
    to provide a comprehensive view of a player for fantasy analysis.
    """
    
    # Core identification
    name: str = Field(..., description="Player's full name")
    yahoo_player_id: Optional[str] = Field(None, description="Yahoo Fantasy player ID")
    mlb_player_id: Optional[int] = Field(None, description="MLB Stats API player ID")
    
    # Position and team information
    eligible_positions: List[str] = Field(default_factory=list, description="Fantasy eligible positions")
    primary_position: Optional[str] = Field(None, description="Primary playing position")
    mlb_team_id: Optional[int] = Field(None, description="MLB team ID")
    mlb_team_name: Optional[str] = Field(None, description="MLB team name")
    
    # Fantasy information
    percent_owned: float = Field(0.0, ge=0.0, le=100.0, description="Ownership percentage in fantasy leagues")
    source: str = Field(..., description="Source of player data (My Team, Waiver, etc.)")
    
    # Pitching-specific information
    is_pitcher: bool = Field(False, description="Whether the player is a pitcher")
    confirmed_start_date: Optional[date] = Field(None, description="Confirmed start date for pitchers")
    potential_second_start: bool = Field(False, description="Whether pitcher has potential for second start")
    
    # Additional metadata
    baseball_savant_url: Optional[str] = Field(None, description="Baseball Savant player page URL")
    last_updated: Optional[date] = Field(None, description="When player data was last updated")
    
    # Enhanced display fields (computed at runtime, not stored)
    profile_image_url: Optional[str] = Field(None, description="Player profile image URL")
    baseball_savant_id: Optional[str] = Field(None, description="Baseball Savant player ID")
    
    @validator('yahoo_player_id', pre=True)
    def validate_yahoo_player_id(cls, v) -> Optional[str]:
        """Convert yahoo_player_id to string if it's an integer."""
        if v is None:
            return None
        return str(v)
    
    @validator('eligible_positions')
    def validate_positions(cls, v: List[str]) -> List[str]:
        """Validate and normalize position codes."""
        valid_positions = {'C', 'CA', '1B', '2B', '3B', 'SS', 'OF', 'LF', 'CF', 'RF', 'DH', 'SP', 'RP', 'P'}
        normalized = []
        for pos in v:
            pos_upper = pos.upper()
            if pos_upper in valid_positions:
                normalized.append(pos_upper)
        return normalized
    
    @validator('is_pitcher', pre=True, always=True)
    def determine_is_pitcher(cls, v: bool, values: Dict[str, Any]) -> bool:
        """Automatically determine if player is a pitcher based on positions."""
        if 'eligible_positions' in values:
            pitcher_positions = {'SP', 'RP', 'P'}
            return any(pos in pitcher_positions for pos in values['eligible_positions'])
        return v
    
    @property
    def display_positions(self) -> str:
        """Return formatted string of eligible positions excluding 'P'."""
        positions = [pos for pos in self.eligible_positions if pos != 'P']
        return '/'.join(positions) if positions else 'N/A'
    
    @property
    def ownership_display(self) -> str:
        """Return formatted ownership percentage."""
        return f"{self.percent_owned:.1f}%"
    
    @property
    def get_profile_image_url(self) -> str:
        """Generate player profile image URL from Baseball Savant URL or MLB ID."""
        if self.profile_image_url:
            return self.profile_image_url
        
        # Try to extract MLB ID from Baseball Savant URL first
        mlb_id = self.extract_mlb_id_from_savant_url()
        if mlb_id:
            # Use the MLB headshot URL format that works
            return f"https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/{mlb_id}/headshot/67/current"
        
        # Fallback to mlb_player_id if available
        if self.mlb_player_id:
            return f"https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/{self.mlb_player_id}/headshot/67/current"
        
        # Generic silhouette placeholder  
        return "https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/generic/headshot/67/current"
    
    @property  
    def get_baseball_savant_id(self) -> Optional[str]:
        """Extract Baseball Savant ID from URL if available."""
        if self.baseball_savant_id:
            return self.baseball_savant_id
        return self.extract_mlb_id_from_savant_url()
    
    def extract_mlb_id_from_savant_url(self) -> Optional[str]:
        """Extract MLB player ID from Baseball Savant URL."""
        if self.baseball_savant_url:
            # URL format: https://baseballsavant.mlb.com/savant-player/firstname-lastname-123456
            # We want to extract the ID (123456)
            import re
            match = re.search(r'-(\d+)(?:\?|$)', self.baseball_savant_url)
            if match:
                return match.group(1)
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert player to dictionary for display purposes."""
        return {
            'name': self.name,
            'positions': self.display_positions,
            'source': self.source,
            'start_date': self.confirmed_start_date.isoformat() if self.confirmed_start_date else None,
            'potential_2nd_start': self.potential_second_start,
            'savant_url': self.baseball_savant_url
        }
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        validate_assignment = True
        extra = "forbid"