"""
Analysis data models for Yahoo Fantasy Baseball application.
"""

from datetime import date, datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from .player import Player


class PitcherAnalysis(BaseModel):
    """
    Represents the analysis results for a pitcher's upcoming starts.
    """
    
    # Player information
    player: Player = Field(..., description="Player object with pitcher details")
    
    # Start analysis
    confirmed_start_date: Optional[date] = Field(None, description="Confirmed start date")
    is_monday_tuesday_start: bool = Field(False, description="Whether start is on Monday or Tuesday")
    potential_second_start: bool = Field(False, description="Whether pitcher has potential for second start")
    second_start_likelihood: float = Field(0.0, ge=0.0, le=1.0, description="Likelihood of second start (0-1)")
    
    # Team context
    team_games_remaining: int = Field(0, ge=0, description="Team games remaining in week")
    team_schedule: List[date] = Field(default_factory=list, description="Team's remaining game dates")
    
    # Fantasy context
    recommendation_score: float = Field(0.0, description="Overall recommendation score")
    recommendation_reason: str = Field("", description="Explanation for recommendation")
    
    # Metadata
    analysis_date: datetime = Field(default_factory=datetime.now, description="When analysis was performed")
    
    @property
    def start_date_display(self) -> str:
        """Return formatted start date."""
        if self.confirmed_start_date:
            return self.confirmed_start_date.strftime('%a, %b %d')
        return "TBD"
    
    @property
    def second_start_display(self) -> str:
        """Return formatted second start likelihood."""
        if self.potential_second_start:
            return f"Likely ({self.second_start_likelihood:.0%})"
        return "Unlikely"
    
    @property
    def priority_score(self) -> int:
        """Calculate priority score for sorting (higher = better)."""
        score = 0
        
        # My team players get highest priority
        if self.player.source == "My Team":
            score += 1000
        
        # Potential second start adds significant value
        if self.potential_second_start:
            score += 500
        
        # Monday/Tuesday starts are preferred
        if self.is_monday_tuesday_start:
            score += 100
        
        # Higher ownership suggests better player
        score += int(self.player.percent_owned)
        
        return score
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert analysis to dictionary for display purposes."""
        return {
            'name': self.player.name,
            'positions': self.player.display_positions,
            'ownership': self.player.ownership_display,
            'source': self.player.source,
            'start_date': self.start_date_display,
            'potential_2nd_start': self.potential_second_start,
            'second_start_likelihood': self.second_start_display,
            'team_games_remaining': self.team_games_remaining,
            'recommendation_score': self.recommendation_score,
            'recommendation_reason': self.recommendation_reason,
            'savant_url': self.player.baseball_savant_url,
            'priority_score': self.priority_score
        }
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        validate_assignment = True
        extra = "forbid"


class FantasyWeek(BaseModel):
    """
    Represents a fantasy baseball week with analysis parameters.
    """
    
    # Week definition
    start_date: date = Field(..., description="Fantasy week start date (Monday)")
    end_date: date = Field(..., description="Fantasy week end date (Sunday)")
    week_number: int = Field(..., ge=1, le=52, description="Fantasy/MLB week number")
    
    # Analysis parameters
    target_days: List[str] = Field(default_factory=lambda: ["Monday", "Tuesday"], 
                                 description="Target days for pitcher analysis")
    
    # Results
    total_pitchers_analyzed: int = Field(0, ge=0, description="Total pitchers analyzed")
    my_team_pitchers: int = Field(0, ge=0, description="My team pitchers found")
    waiver_pitchers: int = Field(0, ge=0, description="Waiver pitchers found")
    
    # Metadata
    analysis_completed: bool = Field(False, description="Whether analysis is complete")
    analysis_duration: Optional[float] = Field(None, description="Analysis duration in seconds")
    
    @property
    def week_display(self) -> str:
        """Return formatted week display."""
        return f"{self.start_date.strftime('%b %d')} - {self.end_date.strftime('%b %d')}"
    
    @property
    def target_dates(self) -> List[date]:
        """Return list of target dates based on target_days."""
        dates = []
        current_date = self.start_date
        
        while current_date <= self.end_date:
            day_name = current_date.strftime('%A')
            if day_name in self.target_days:
                dates.append(current_date)
            current_date = current_date.replace(day=current_date.day + 1)
        
        return dates
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert fantasy week to dictionary for display purposes."""
        return {
            'week_number': self.week_number,
            'week_display': self.week_display,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'target_days': self.target_days,
            'total_pitchers': self.total_pitchers_analyzed,
            'my_team_pitchers': self.my_team_pitchers,
            'waiver_pitchers': self.waiver_pitchers,
            'analysis_completed': self.analysis_completed,
            'analysis_duration': self.analysis_duration
        }
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        validate_assignment = True
        extra = "forbid"