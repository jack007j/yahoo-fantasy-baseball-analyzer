"""
Utility functions for text processing, URL generation, and date calculations.
"""

from .text_utils import (
    slugify,
    normalize_player_name,
    extract_first_last_name,
    calculate_name_similarity,
    format_player_display_name,
    clean_team_name,
    truncate_text,
    format_percentage,
    parse_yahoo_id
)

from .url_utils import (
    create_savant_link,
    create_yahoo_player_link,
    create_mlb_player_link,
    create_fangraphs_link,
    create_baseball_reference_link,
    create_rotowire_link,
    create_espn_player_link,
    validate_url,
    create_player_links_dict,
    create_team_schedule_link,
    create_league_standings_link,
    create_waiver_wire_link,
    shorten_url_display
)

from .date_utils import (
    get_next_fantasy_week,
    get_current_fantasy_week,
    get_fantasy_week_for_date,
    get_fantasy_week_number,
    get_target_analysis_dates,
    is_monday_or_tuesday,
    get_days_until_date,
    format_date_display,
    format_date_range,
    get_season_dates,
    is_within_season,
    get_week_dates_list,
    parse_date_string,
    get_relative_date_description,
    get_business_days_between
)

__all__ = [
    # Text utilities
    "slugify",
    "normalize_player_name",
    "extract_first_last_name", 
    "calculate_name_similarity",
    "format_player_display_name",
    "clean_team_name",
    "truncate_text",
    "format_percentage",
    "parse_yahoo_id",
    
    # URL utilities
    "create_savant_link",
    "create_yahoo_player_link",
    "create_mlb_player_link",
    "create_fangraphs_link",
    "create_baseball_reference_link",
    "create_rotowire_link",
    "create_espn_player_link",
    "validate_url",
    "create_player_links_dict",
    "create_team_schedule_link",
    "create_league_standings_link",
    "create_waiver_wire_link",
    "shorten_url_display",
    
    # Date utilities
    "get_next_fantasy_week",
    "get_current_fantasy_week",
    "get_fantasy_week_for_date",
    "get_fantasy_week_number",
    "get_target_analysis_dates",
    "is_monday_or_tuesday",
    "get_days_until_date",
    "format_date_display",
    "format_date_range",
    "get_season_dates",
    "is_within_season",
    "get_week_dates_list",
    "parse_date_string",
    "get_relative_date_description",
    "get_business_days_between"
]