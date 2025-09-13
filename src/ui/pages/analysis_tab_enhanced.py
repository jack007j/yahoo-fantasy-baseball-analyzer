"""
Enhanced analysis tab with player profile pictures and improved visual design.

Displays Monday/Tuesday starter analysis with player cards and images.
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import date, timedelta

from ...models.analysis import PitcherAnalysis, FantasyWeek
from ...services.analysis_service import AnalysisService
from ...api.yahoo_client import YahooFantasyClient
from ...api.mlb_client import MLBStatsClient
from ...services.cache_service import CacheService
from ...core.exceptions import AnalysisError, APIError
from ..components.sidebar_enhanced import get_sidebar_state


def render_enhanced_analysis_tab() -> None:
    """Render enhanced analysis tab with pitcher cards and profile images."""
    # Simple plain header - h3 is smaller than main title
    st.markdown("""
        <style>
        /* Reduce spacing around h3 headers */
        .stMarkdown h3 {
            font-size: 1.3rem; /* About 20-21px */
            font-weight: 600;
            margin-top: -0.5rem !important;
            margin-bottom: 0.25rem !important;
            padding: 0 !important;
        }

        /* Reduce space in the containing div */
        div[data-testid="stVerticalBlock"] > div:has(h3) {
            margin-top: 0 !important;
            margin-bottom: 0 !important;
            padding-top: 0 !important;
            padding-bottom: 0 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    st.markdown("### Early Week Starters")
    
    # Check configuration
    sidebar_state = get_sidebar_state()
    team_key = sidebar_state.get('team_key')
    
    if not team_key:
        _show_analysis_placeholder()
        return
    
    # Analysis controls with mobile-friendly layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        pass
    
    with col2:
        if st.button("🔍 Analyze", type="primary", use_container_width=True):
            st.session_state['run_analysis'] = True
            st.session_state.pop('analysis_status', None)
    
    # Run analysis if requested
    if st.session_state.get('run_analysis', False):
        _run_enhanced_analysis(team_key, sidebar_state['analysis_settings'])
        st.session_state['run_analysis'] = False
    
    # Display results
    if 'analysis_results' in st.session_state:
        _display_enhanced_analysis_results(
            st.session_state['analysis_results']['fantasy_week'],
            st.session_state['analysis_results']['pitcher_analyses'],
            sidebar_state['analysis_settings']
        )
    else:
        _show_analysis_placeholder()


def _run_enhanced_analysis(team_key: str, settings: Dict[str, Any]) -> None:
    """Run analysis with enhanced data including player images."""
    try:
        with st.spinner("⚾ Analyzing starting pitchers..."):
            # Initialize services
            yahoo_client = YahooFantasyClient()
            mlb_client = MLBStatsClient()
            cache_service = CacheService()
            analysis_service = AnalysisService(yahoo_client, mlb_client, cache_service)
            
            # Run analysis
            fantasy_week, pitcher_analyses = analysis_service.analyze_next_fantasy_week(team_key)
            
            # Players already have image URL properties
            
            # Filter results
            filtered_analyses = _filter_analyses(pitcher_analyses, settings)
            
            # Store results
            st.session_state['analysis_results'] = {
                'fantasy_week': fantasy_week,
                'pitcher_analyses': filtered_analyses,
                'timestamp': pd.Timestamp.now()
            }
            
            st.session_state['analysis_status'] = 'success'
    
    except Exception as e:
        st.session_state['analysis_status'] = f"Error: {str(e)}"


# Image URL generation moved to Player model property


def _filter_analyses(analyses: List[PitcherAnalysis], settings: Dict[str, Any]) -> List[PitcherAnalysis]:
    """Filter analysis results based on settings."""
    filtered = analyses
    
    # Apply ownership filter
    ownership_threshold = settings.get('ownership_threshold', 0)
    if ownership_threshold > 0:
        filtered = [a for a in filtered if a.player.percent_owned >= ownership_threshold]
    
    # Apply waiver filter
    if not settings.get('show_waiver_players', True):
        filtered = [a for a in filtered if a.player.source != 'Waiver']
    
    return filtered


def _display_enhanced_analysis_results(
    fantasy_week: FantasyWeek,
    pitcher_analyses: List[PitcherAnalysis],
    settings: Dict[str, Any]
) -> None:
    """Display enhanced analysis results with pitcher cards."""

    # Week header - just dates
    _display_week_header(fantasy_week)

    if not pitcher_analyses:
        st.warning("No confirmed starters found for your criteria.")
        return

    # Display all pitchers in one list
    _display_pitcher_cards(pitcher_analyses, settings)


def _display_week_header(fantasy_week: FantasyWeek) -> None:
    """Display fantasy week header."""
    st.markdown(f"**📅 {fantasy_week.week_display}**")
    st.caption(f"Analyzing: {', '.join(fantasy_week.target_days)} • ⭐ = Two-start potential")


def _display_summary_metrics(fantasy_week: FantasyWeek, analyses: List[PitcherAnalysis]) -> None:
    """Display summary metrics."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Starters", len(analyses))
    
    with col2:
        st.metric("My Team", fantasy_week.my_team_pitchers)
    
    with col3:
        st.metric("Waiver Wire", fantasy_week.waiver_pitchers)
    
    with col4:
        second_starts = len([p for p in analyses if p.potential_second_start])
        st.metric("2nd Starts", second_starts)


def _display_pitcher_cards(pitchers: List[PitcherAnalysis], settings: Dict[str, Any]) -> None:
    """Display pitcher analysis cards with profile images."""
    
    # Sort by recommendation priority
    pitchers.sort(key=lambda p: (
        p.player.source == "My Team",  # My team first
        p.potential_second_start,  # Second starters next
        -p.player.percent_owned  # Then by ownership
    ), reverse=True)
    
    # Display in grid
    cols_per_row = 2  # 2 columns for better mobile experience
    
    for i in range(0, len(pitchers), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            if i + j < len(pitchers):
                with col:
                    _display_pitcher_analysis_card(pitchers[i + j])


def _display_pitcher_analysis_card(analysis: PitcherAnalysis) -> None:
    """Display compact mobile-optimized pitcher analysis card."""
    player = analysis.player
    import urllib.parse

    # Build source badge
    if player.source == "My Team":
        source_badge = '✅ Team'
    else:
        source_badge = '🔄 Waiver'

    # Add star if second start potential
    second_start = '⭐' if analysis.potential_second_start else ''

    # Build Savant link
    if player.baseball_savant_url:
        savant_link = player.baseball_savant_url
        savant_text = "📊 Savant Profile"
    else:
        search_name = urllib.parse.quote(player.name)
        savant_link = f"https://baseballsavant.mlb.com/player_search?player_search={search_name}"
        savant_text = "🔍 Savant Profile"

    # Use HTML for consistent single-line layout with proper flex properties
    card_html = f'''
    <div style="display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid #e0e0e0;">
        <img src="{player.get_profile_image_url}" style="height: 40px; border-radius: 6px; flex: 0 0 auto; object-fit: contain;">
        <div style="flex: 1 1 auto; min-width: 0; overflow: hidden;">
            <div style="font-weight: 600; font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{player.name} {second_start}</div>
            <div style="font-size: 12px; color: #666; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">📅 {analysis.start_date_display} • {source_badge} • {player.display_positions}</div>
        </div>
        <a href="{savant_link}" target="_blank" style="background: rgba(0,0,0,0.7); color: white; padding: 8px 12px; border-radius: 6px; text-decoration: none; font-size: 13px; flex: 0 0 auto; white-space: nowrap; display: flex; align-items: center; justify-content: center;">{savant_text}</a>
    </div>
    '''

    st.markdown(card_html, unsafe_allow_html=True)




def _show_analysis_placeholder() -> None:
    """Show placeholder content."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **🎯 What this analysis provides:**
        - Confirmed Monday/Tuesday starters
        - Baseball Savant links
        - Second start potential
        """)
    
    with col2:
        st.info("""
        **⚾ How to use:**
        1. Configure team key in sidebar
        2. Select target days
        3. Click "Analyze" button
        4. Review pitcher cards
        5. Click Savant links for stats
        """)