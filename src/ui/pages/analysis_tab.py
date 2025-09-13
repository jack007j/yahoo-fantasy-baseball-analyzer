"""
Analysis tab for Yahoo Fantasy Baseball Streamlit application.

Displays Monday/Tuesday starter analysis results with professional formatting.
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
from ..components.sidebar import show_configuration_status, get_sidebar_state


def render_analysis_tab() -> None:
    """Render the analysis tab with starter analysis results."""
    st.header("📊 Monday/Tuesday Starter Analysis")
    
    # Check if configuration is complete
    if show_configuration_status():
        return
    
    sidebar_state = get_sidebar_state()
    team_key = sidebar_state.get('team_key')
    
    if not team_key:
        return
    
    # Analysis controls
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown("*Find the best confirmed Monday/Tuesday starting pitchers for your fantasy team*")
    
    with col2:
        if st.button("🔄 Run Analysis", type="primary", use_container_width=True):
            st.session_state['run_analysis'] = True
    
    with col3:
        if st.button("🗑️ Clear Cache", key="analysis_clear_cache", use_container_width=True):
            _clear_analysis_cache()
            st.success("Cache cleared!")
    
    # Run analysis if requested
    if st.session_state.get('run_analysis', False):
        _run_analysis(team_key, sidebar_state['analysis_settings'])
        st.session_state['run_analysis'] = False
    
    # Display results if available
    if 'analysis_results' in st.session_state:
        _display_analysis_results(
            st.session_state['analysis_results']['fantasy_week'],
            st.session_state['analysis_results']['pitcher_analyses'],
            sidebar_state['analysis_settings']
        )
    else:
        _show_analysis_placeholder()


def _run_analysis(team_key: str, settings: Dict[str, Any]) -> None:
    """Run the analysis and store results in session state."""
    try:
        with st.spinner("🔍 Analyzing Monday/Tuesday starters..."):
            # Initialize services
            yahoo_client = YahooFantasyClient()
            mlb_client = MLBStatsClient()
            cache_service = CacheService()
            analysis_service = AnalysisService(yahoo_client, mlb_client, cache_service)
            
            # Run analysis
            fantasy_week, pitcher_analyses = analysis_service.analyze_next_fantasy_week(team_key)
            
            # Filter results based on settings
            filtered_analyses = _filter_analyses(pitcher_analyses, settings)
            
            # Store results
            st.session_state['analysis_results'] = {
                'fantasy_week': fantasy_week,
                'pitcher_analyses': filtered_analyses,
                'timestamp': pd.Timestamp.now()
            }
            
            st.success(f"✅ Analysis complete! Found {len(filtered_analyses)} matching pitchers.")
    
    except AnalysisError as e:
        st.error(f"❌ Analysis failed: {str(e)}")
    except APIError as e:
        st.error(f"❌ API error: {str(e)}")
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")


def _filter_analyses(analyses: List[PitcherAnalysis], settings: Dict[str, Any]) -> List[PitcherAnalysis]:
    """Filter analysis results based on user settings."""
    filtered = analyses
    
    # Filter by ownership threshold
    ownership_threshold = settings.get('ownership_threshold', 0)
    if ownership_threshold > 0:
        filtered = [a for a in filtered if a.player.percent_owned >= ownership_threshold]
    
    # Filter by waiver players setting
    if not settings.get('show_waiver_players', True):
        filtered = [a for a in filtered if a.player.source != 'Waiver']
    
    # Filter by second starts setting
    if not settings.get('include_second_starts', True):
        # Still include all, but don't highlight second starts
        pass
    
    return filtered


def _display_analysis_results(
    fantasy_week: FantasyWeek, 
    pitcher_analyses: List[PitcherAnalysis],
    settings: Dict[str, Any]
) -> None:
    """Display the analysis results with professional formatting."""
    
    # Fantasy week header
    _display_fantasy_week_header(fantasy_week)
    
    if not pitcher_analyses:
        st.warning("No confirmed Monday/Tuesday starters found matching your criteria.")
        return
    
    # Summary metrics
    _display_summary_metrics(fantasy_week, pitcher_analyses)
    
    # Group by source (My Team vs Waiver)
    my_team_pitchers = [p for p in pitcher_analyses if p.player.source == "My Team"]
    waiver_pitchers = [p for p in pitcher_analyses if p.player.source == "Waiver"]
    
    # Display My Team pitchers
    if my_team_pitchers:
        _display_pitcher_group("👥 My Team - Confirmed Starters", my_team_pitchers, settings)
    
    # Display Waiver pitchers
    if waiver_pitchers and settings.get('show_waiver_players', True):
        _display_pitcher_group("🔄 Waiver Wire - Available Starters", waiver_pitchers, settings)
    


def _display_fantasy_week_header(fantasy_week: FantasyWeek) -> None:
    """Display fantasy week information header."""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader(f"📅 Fantasy Week: {fantasy_week.week_display}")
        st.caption(f"Week {fantasy_week.week_number} • Target Days: {', '.join(fantasy_week.target_days)}")
    
    with col2:
        st.metric("Total Found", fantasy_week.total_pitchers_analyzed)


def _display_summary_metrics(fantasy_week: FantasyWeek, pitcher_analyses: List[PitcherAnalysis]) -> None:
    """Display summary metrics in compact columns."""
    st.markdown("##### 📊 Quick Stats")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"**My Team:** {fantasy_week.my_team_pitchers}")
        st.markdown(f"**Waiver:** {fantasy_week.waiver_pitchers}")
    
    with col2:
        second_start_count = len([p for p in pitcher_analyses if p.potential_second_start])
        st.markdown(f"**2nd Starts:** {second_start_count}")
        
    with col3:
        monday_count = len([p for p in pitcher_analyses if p.confirmed_start_date and p.confirmed_start_date.weekday() == 0])
        tuesday_count = len([p for p in pitcher_analyses if p.confirmed_start_date and p.confirmed_start_date.weekday() == 1])
        st.markdown(f"**Mon/Tue:** {monday_count}/{tuesday_count}")
    
    st.divider()


def _display_pitcher_group(title: str, pitchers: List[PitcherAnalysis], settings: Dict[str, Any]) -> None:
    """Display a group of pitchers with consistent formatting."""
    st.subheader(title)
    
    if not pitchers:
        st.info("No pitchers found in this category.")
        return
    
    # Create DataFrame for display
    display_data = []
    for analysis in pitchers:
        row = {
            'Player': analysis.player.name,
            'Positions': analysis.player.display_positions,
            'Team': analysis.player.mlb_team_name or 'Unknown',
            'Start Date': analysis.start_date_display,
            'Ownership': analysis.player.ownership_display,
            'Potential 2nd': "✅ Likely" if analysis.potential_second_start else "❌ Unlikely",
            'Recommendation': analysis.recommendation_reason,
            'Baseball Savant': analysis.player.baseball_savant_url or ""
        }
        display_data.append(row)
    
    df = pd.DataFrame(display_data)
    
    # Display as interactive table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            'Player': st.column_config.TextColumn('Player', width='medium'),
            'Positions': st.column_config.TextColumn('Pos', width='small'),
            'Team': st.column_config.TextColumn('MLB Team', width='small'),
            'Start Date': st.column_config.TextColumn('Start Date', width='medium'),
            'Ownership': st.column_config.TextColumn('Own %', width='small'),
            'Potential 2nd': st.column_config.TextColumn('2nd Start', width='medium'),
            'Recommendation': st.column_config.TextColumn('Notes', width='large'),
            'Baseball Savant': st.column_config.LinkColumn(
                'Savant Link',
                help="Click to view Baseball Savant player page",
                width='medium'
            )
        }
    )
    
    # Individual pitcher cards for detailed view
    with st.expander(f"📋 Detailed View ({len(pitchers)} pitchers)", expanded=False):
        for analysis in pitchers:
            _display_pitcher_card(analysis, settings)


def _display_pitcher_card(analysis: PitcherAnalysis, settings: Dict[str, Any]) -> None:
    """Display individual pitcher card with detailed information."""
    player = analysis.player
    
    # Card container
    with st.container():
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
        
        with col1:
            st.markdown(f"**{player.name}** ({player.display_positions})")
            if player.baseball_savant_url:
                st.markdown(f"[📊 Baseball Savant]({player.baseball_savant_url})")
        
        with col2:
            st.markdown(f"**Start:** {analysis.start_date_display}")
            st.markdown(f"**Team:** {player.mlb_team_name or 'Unknown'}")
        
        with col3:
            st.markdown(f"**Ownership:** {player.ownership_display}")
            st.markdown(f"**Source:** {player.source}")
        
        with col4:
            if analysis.potential_second_start:
                st.success("🔄 Potential 2nd Start")
            else:
                st.info("Single Start Expected")
        
        if analysis.recommendation_reason:
            st.caption(f"💡 {analysis.recommendation_reason}")
        
        st.divider()




def _show_analysis_placeholder() -> None:
    """Show placeholder content when no analysis has been run."""
    st.info("""
    🎯 **Ready to analyze Monday/Tuesday starters!**
    
    Click the "Run Analysis" button above to:
    - Find confirmed probable starters for Monday/Tuesday
    - Identify potential second starts in the week
    - Compare your roster vs. waiver wire options
    - Get direct links to Baseball Savant player pages
    
    The analysis will show results for the upcoming fantasy week.
    """)
    
    # Show example of what the analysis will look like
    with st.expander("📋 Preview: What you'll see", expanded=False):
        st.markdown("""
        **Fantasy Week Information:**
        - Week dates and target days
        - Summary metrics and counts
        
        **My Team Section:**
        - Confirmed starters already on your roster
        - Start dates and potential second starts
        - Ownership percentages and recommendations
        
        **Waiver Wire Section:**
        - Available starters you can pick up
        - Sorted by priority and ownership
        - Direct links to player statistics
        
        **Analysis Insights:**
        - Key recommendations and observations
        - Low-owned options worth considering
        - Second start opportunities
        """)


def _clear_analysis_cache() -> None:
    """Clear analysis cache and session state."""
    # Clear session state
    keys_to_clear = ['analysis_results', 'run_analysis']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    # Clear any cached data
    st.cache_data.clear()