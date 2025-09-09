"""
Date and time utilities for the Yahoo Fantasy Baseball application.
"""

from datetime import date, datetime, timedelta
from typing import List, Tuple, Optional
import calendar

from ..core.constants import FANTASY_WEEK_START_DAY, FANTASY_WEEK_LENGTH_DAYS


def get_next_fantasy_week() -> Tuple[date, date]:
    """
    Calculate the next fantasy week start and end dates.
    
    Fantasy weeks typically run Monday to Sunday.
    
    Returns:
        Tuple of (start_date, end_date) for next fantasy week
        
    Examples:
        >>> # If today is Wednesday, returns next Monday-Sunday
        >>> start, end = get_next_fantasy_week()
        >>> start.weekday()  # 0 (Monday)
        >>> (end - start).days  # 6 (Sunday is 6 days after Monday)
    """
    today = date.today()
    
    # Calculate days until next Monday
    days_until_next_monday = (7 - today.weekday()) % 7
    if days_until_next_monday == 0:
        days_until_next_monday = 7  # If today is Monday, get next Monday
    
    next_monday = today + timedelta(days=days_until_next_monday)
    next_sunday = next_monday + timedelta(days=6)
    
    return next_monday, next_sunday


def get_current_fantasy_week() -> Tuple[date, date]:
    """
    Calculate the current fantasy week start and end dates.
    
    Returns:
        Tuple of (start_date, end_date) for current fantasy week
    """
    today = date.today()
    
    # Calculate days since last Monday
    days_since_monday = today.weekday()
    current_monday = today - timedelta(days=days_since_monday)
    current_sunday = current_monday + timedelta(days=6)
    
    return current_monday, current_sunday


def get_fantasy_week_for_date(target_date: date) -> Tuple[date, date]:
    """
    Get the fantasy week that contains the given date.
    
    Args:
        target_date: Date to find fantasy week for
        
    Returns:
        Tuple of (start_date, end_date) for fantasy week containing target_date
    """
    # Calculate days since last Monday
    days_since_monday = target_date.weekday()
    week_monday = target_date - timedelta(days=days_since_monday)
    week_sunday = week_monday + timedelta(days=6)
    
    return week_monday, week_sunday


def get_fantasy_week_number(week_start_date: date, season_start: Optional[date] = None) -> int:
    """
    Calculate fantasy week number for a given week.
    
    Args:
        week_start_date: Monday start date of the fantasy week
        season_start: First Monday of fantasy season (defaults to first Monday of April)
        
    Returns:
        Fantasy week number (1-based)
    """
    if season_start is None:
        # Default to first Monday of April
        year = week_start_date.year
        april_first = date(year, 4, 1)
        days_to_monday = (7 - april_first.weekday()) % 7
        season_start = april_first + timedelta(days=days_to_monday)
    
    # Calculate weeks since season start
    days_diff = (week_start_date - season_start).days
    week_number = (days_diff // 7) + 1
    
    return max(1, week_number)


def get_target_analysis_dates(week_start: date, target_days: List[str] = None) -> List[date]:
    """
    Get specific dates within a fantasy week for analysis.
    
    Args:
        week_start: Monday start date of fantasy week
        target_days: List of day names to target (default: ["Monday", "Tuesday"])
        
    Returns:
        List of dates matching target days
    """
    if target_days is None:
        target_days = ["Monday", "Tuesday"]
    
    target_dates = []
    
    for i in range(7):  # Check each day of the week
        current_date = week_start + timedelta(days=i)
        day_name = current_date.strftime('%A')
        
        if day_name in target_days:
            target_dates.append(current_date)
    
    return target_dates


def is_monday_or_tuesday(target_date: date) -> bool:
    """
    Check if a date falls on Monday or Tuesday.
    
    Args:
        target_date: Date to check
        
    Returns:
        True if date is Monday or Tuesday
    """
    return target_date.weekday() in [0, 1]  # 0=Monday, 1=Tuesday


def get_days_until_date(target_date: date) -> int:
    """
    Calculate days from today until target date.
    
    Args:
        target_date: Target date
        
    Returns:
        Number of days (negative if in past)
    """
    today = date.today()
    return (target_date - today).days


def format_date_display(target_date: date, include_weekday: bool = True) -> str:
    """
    Format date for display in UI.
    
    Args:
        target_date: Date to format
        include_weekday: Whether to include weekday name
        
    Returns:
        Formatted date string
        
    Examples:
        >>> format_date_display(date(2024, 4, 15), True)
        'Mon, Apr 15'
        >>> format_date_display(date(2024, 4, 15), False)
        'Apr 15'
    """
    if include_weekday:
        return target_date.strftime('%a, %b %d')
    else:
        return target_date.strftime('%b %d')


def format_date_range(start_date: date, end_date: date) -> str:
    """
    Format date range for display.
    
    Args:
        start_date: Range start date
        end_date: Range end date
        
    Returns:
        Formatted date range string
        
    Examples:
        >>> format_date_range(date(2024, 4, 15), date(2024, 4, 21))
        'Apr 15 - Apr 21'
    """
    if start_date.month == end_date.month:
        return f"{start_date.strftime('%b %d')} - {end_date.strftime('%d')}"
    else:
        return f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d')}"


def get_season_dates(year: int) -> Tuple[date, date]:
    """
    Get approximate MLB season start and end dates.
    
    Args:
        year: Season year
        
    Returns:
        Tuple of (season_start, season_end)
    """
    # MLB season typically runs late March/early April to late September/early October
    season_start = date(year, 3, 28)  # Approximate opening day
    season_end = date(year, 10, 1)    # Approximate regular season end
    
    return season_start, season_end


def is_within_season(target_date: date, year: Optional[int] = None) -> bool:
    """
    Check if date falls within MLB season.
    
    Args:
        target_date: Date to check
        year: Season year (defaults to target_date year)
        
    Returns:
        True if date is within season
    """
    if year is None:
        year = target_date.year
    
    season_start, season_end = get_season_dates(year)
    return season_start <= target_date <= season_end


def get_week_dates_list(start_date: date, num_weeks: int = 1) -> List[Tuple[date, date]]:
    """
    Get list of fantasy week date ranges.
    
    Args:
        start_date: Starting Monday
        num_weeks: Number of weeks to generate
        
    Returns:
        List of (start_date, end_date) tuples
    """
    weeks = []
    current_monday = start_date
    
    for _ in range(num_weeks):
        current_sunday = current_monday + timedelta(days=6)
        weeks.append((current_monday, current_sunday))
        current_monday += timedelta(days=7)
    
    return weeks


def parse_date_string(date_str: str) -> Optional[date]:
    """
    Parse date string in various formats.
    
    Args:
        date_str: Date string to parse
        
    Returns:
        Parsed date or None if invalid
    """
    if not date_str:
        return None
    
    # Common date formats to try
    formats = [
        '%Y-%m-%d',      # 2024-04-15
        '%m/%d/%Y',      # 04/15/2024
        '%m-%d-%Y',      # 04-15-2024
        '%Y/%m/%d',      # 2024/04/15
        '%b %d, %Y',     # Apr 15, 2024
        '%B %d, %Y',     # April 15, 2024
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    
    return None


def get_relative_date_description(target_date: date) -> str:
    """
    Get relative description of date (e.g., "today", "tomorrow", "in 3 days").
    
    Args:
        target_date: Date to describe
        
    Returns:
        Relative date description
    """
    today = date.today()
    days_diff = (target_date - today).days
    
    if days_diff == 0:
        return "today"
    elif days_diff == 1:
        return "tomorrow"
    elif days_diff == -1:
        return "yesterday"
    elif days_diff > 1:
        return f"in {days_diff} days"
    else:
        return f"{abs(days_diff)} days ago"


def get_business_days_between(start_date: date, end_date: date) -> int:
    """
    Calculate number of business days (Monday-Friday) between dates.
    
    Args:
        start_date: Start date (inclusive)
        end_date: End date (exclusive)
        
    Returns:
        Number of business days
    """
    business_days = 0
    current_date = start_date
    
    while current_date < end_date:
        if current_date.weekday() < 5:  # Monday=0, Friday=4
            business_days += 1
        current_date += timedelta(days=1)
    
    return business_days