"""
Team data model for Yahoo Fantasy Baseball application.
"""

from datetime import date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class MLBTeam(BaseModel):
    """
    Represents an MLB team with schedule and game information.
    """
    
    # Core identification
    team_id: int = Field(..., description="MLB Stats API team ID")
    name: str = Field(..., description="Team full name")
    abbreviation: Optional[str] = Field(None, description="Team abbreviation (e.g., 'NYY')")
    
    # Division and league information
    division: Optional[str] = Field(None, description="Division name")
    league: Optional[str] = Field(None, description="League (AL/NL)")
    
    # Schedule information
    games_this_week: List[date] = Field(default_factory=list, description="Game dates for current week")
    next_game_date: Optional[date] = Field(None, description="Next scheduled game date")
    
    @property
    def games_count_this_week(self) -> int:
        """Return number of games scheduled for this week."""
        return len(self.games_this_week)
    
    def has_game_on_date(self, game_date: date) -> bool:
        """Check if team has a game on specific date."""
        return game_date in self.games_this_week
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert team to dictionary for display purposes."""
        return {
            'team_id': self.team_id,
            'name': self.name,
            'abbreviation': self.abbreviation,
            'division': self.division,
            'league': self.league,
            'games_this_week': len(self.games_this_week),
            'next_game': self.next_game_date.isoformat() if self.next_game_date else None
        }
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        validate_assignment = True
        extra = "forbid"


class FantasyTeam(BaseModel):
    """
    Represents a Yahoo Fantasy Baseball team.
    """
    
    # Core identification
    team_key: str = Field(..., description="Yahoo Fantasy team key")
    team_id: str = Field(..., description="Yahoo Fantasy team ID")
    name: str = Field(..., description="Fantasy team name")
    
    # League information
    league_id: str = Field(..., description="Yahoo Fantasy league ID")
    league_name: Optional[str] = Field(None, description="Fantasy league name")
    
    # Team details
    manager_name: Optional[str] = Field(None, description="Team manager name")
    logo_url: Optional[str] = Field(None, description="Team logo URL")
    
    # Performance metrics
    wins: int = Field(0, ge=0, description="Season wins")
    losses: int = Field(0, ge=0, description="Season losses")
    ties: int = Field(0, ge=0, description="Season ties")
    winning_percentage: float = Field(0.0, ge=0.0, le=1.0, description="Winning percentage")
    
    # Standings
    rank: Optional[int] = Field(None, ge=1, description="Current league rank")
    points_for: float = Field(0.0, description="Total points scored")
    points_against: float = Field(0.0, description="Total points allowed")
    
    @property
    def record_display(self) -> str:
        """Return formatted win-loss record."""
        if self.ties > 0:
            return f"{self.wins}-{self.losses}-{self.ties}"
        return f"{self.wins}-{self.losses}"
    
    @property
    def winning_percentage_display(self) -> str:
        """Return formatted winning percentage."""
        return f"{self.winning_percentage:.3f}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert fantasy team to dictionary for display purposes."""
        return {
            'team_key': self.team_key,
            'team_id': self.team_id,
            'name': self.name,
            'manager': self.manager_name,
            'record': self.record_display,
            'winning_pct': self.winning_percentage_display,
            'rank': self.rank,
            'points_for': self.points_for,
            'points_against': self.points_against
        }
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        validate_assignment = True
        extra = "forbid"