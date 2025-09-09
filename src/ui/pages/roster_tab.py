"""
Roster tab for Yahoo Fantasy Baseball Streamlit application.

Displays user's team roster in organized fantasy sports app style layout.
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional
from collections import defaultdict

from ...models.player import Player
from ...services.analysis_service import AnalysisService
from ...api.yahoo_client import YahooFantasyClient
from ...api.mlb_client import MLBStatsClient
from ...services.cache_service import CacheService
from ...core.exceptions import AnalysisError, APIError
from ..components.sidebar import show_configuration_status, get_sidebar_state


def render_roster_tab() -> None:
    """Render the roster tab with team roster display."""
    st.header("👥 My Team Roster")
    
    # Check if configuration is complete
    if show_configuration_status():
        return
    
    sidebar_state = get_sidebar_state()
    team_key = sidebar_state.get('team_key')
    
    if not team_key:
        return
    
    # Roster controls
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown("*View your complete fantasy baseball roster with player details and statistics*")
    
    with col2:
        if st.button("🔄 Refresh Roster", type="primary", use_container_width=True):
            st.session_state['refresh_roster'] = True
    
    with col3:
        if st.button("🗑️ Clear Cache", key="roster_clear_cache", use_container_width=True):
            _clear_roster_cache()
            st.success("Cache cleared!")
    
    # Load roster if requested or not already loaded
    if st.session_state.get('refresh_roster', False) or 'roster_data' not in st.session_state:
        _load_roster_data(team_key)
        st.session_state['refresh_roster'] = False
    
    # Display roster if available
    if 'roster_data' in st.session_state:
        _display_roster(st.session_state['roster_data'])
    else:
        _show_roster_placeholder()


def _load_roster_data(team_key: str) -> None:
    """Load roster data and store in session state."""
    try:
        with st.spinner("📋 Loading your team roster..."):
            # Initialize services
            yahoo_client = YahooFantasyClient()
            mlb_client = MLBStatsClient()
            cache_service = CacheService()
            analysis_service = AnalysisService(yahoo_client, mlb_client, cache_service)
            
            # Get roster data
            roster_players = analysis_service.get_team_roster(team_key)
            
            # Store results
            st.session_state['roster_data'] = {
                'players': roster_players,
                'timestamp': pd.Timestamp.now()
            }
            
            st.success(f"✅ Roster loaded! Found {len(roster_players)} players.")
    
    except AnalysisError as e:
        st.error(f"❌ Failed to load roster: {str(e)}")
    except APIError as e:
        st.error(f"❌ API error: {str(e)}")
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")


def _display_roster(roster_data: Dict[str, Any]) -> None:
    """Display the complete roster with organized layout."""
    players = roster_data['players']
    
    if not players:
        st.warning("No players found on your roster.")
        return
    
    # Roster summary
    _display_roster_summary(players)
    
    # Group players by position type
    pitchers, batters = _group_players_by_type(players)
    
    # Display position groups
    if pitchers:
        _display_pitcher_section(pitchers)
    
    if batters:
        _display_batter_section(batters)
    
    # Roster insights
    _display_roster_insights(players)


def _display_roster_summary(players: List[Player]) -> None:
    """Display roster summary metrics."""
    st.subheader("📊 Roster Summary")
    
    # Calculate metrics
    total_players = len(players)
    pitchers = [p for p in players if p.is_pitcher]
    batters = [p for p in players if not p.is_pitcher]
    
    # Ownership stats
    avg_ownership = sum(p.percent_owned for p in players) / len(players) if players else 0
    high_owned = len([p for p in players if p.percent_owned > 75])
    low_owned = len([p for p in players if p.percent_owned < 25])
    
    # Display metrics in columns
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Players", total_players)
    
    with col2:
        st.metric("Pitchers", len(pitchers))
    
    with col3:
        st.metric("Batters", len(batters))
    
    with col4:
        st.metric("Avg Ownership", f"{avg_ownership:.1f}%")
    
    with col5:
        st.metric("High Owned (>75%)", high_owned)


def _group_players_by_type(players: List[Player]) -> tuple[List[Player], List[Player]]:
    """Group players into pitchers and batters."""
    pitchers = []
    batters = []
    
    for player in players:
        if player.is_pitcher:
            pitchers.append(player)
        else:
            batters.append(player)
    
    # Sort by ownership percentage (descending)
    pitchers.sort(key=lambda p: p.percent_owned, reverse=True)
    batters.sort(key=lambda p: p.percent_owned, reverse=True)
    
    return pitchers, batters


def _display_pitcher_section(pitchers: List[Player]) -> None:
    """Display pitchers section with detailed cards."""
    st.subheader("⚾ Pitchers")
    
    # Group pitchers by position
    starters = [p for p in pitchers if 'SP' in p.eligible_positions]
    relievers = [p for p in pitchers if 'RP' in p.eligible_positions and 'SP' not in p.eligible_positions]
    
    # Tabs for different pitcher types
    if starters and relievers:
        tab1, tab2 = st.tabs([f"Starting Pitchers ({len(starters)})", f"Relief Pitchers ({len(relievers)})"])
        
        with tab1:
            _display_player_cards(starters, "pitcher")
        
        with tab2:
            _display_player_cards(relievers, "pitcher")
    
    elif starters:
        st.markdown(f"**Starting Pitchers ({len(starters)})**")
        _display_player_cards(starters, "pitcher")
    
    elif relievers:
        st.markdown(f"**Relief Pitchers ({len(relievers)})**")
        _display_player_cards(relievers, "pitcher")


def _display_batter_section(batters: List[Player]) -> None:
    """Display batters section organized by position groups."""
    st.subheader("🏏 Position Players")
    
    # Group by position categories
    position_groups = _group_batters_by_position(batters)
    
    # Create tabs for position groups
    if len(position_groups) > 1:
        tab_names = [f"{group} ({len(players)})" for group, players in position_groups.items()]
        tabs = st.tabs(tab_names)
        
        for tab, (group_name, group_players) in zip(tabs, position_groups.items()):
            with tab:
                _display_player_cards(group_players, "batter")
    else:
        # Single group, display directly
        for group_name, group_players in position_groups.items():
            st.markdown(f"**{group_name} ({len(group_players)})**")
            _display_player_cards(group_players, "batter")


def _group_batters_by_position(batters: List[Player]) -> Dict[str, List[Player]]:
    """Group batters by position categories."""
    position_groups = defaultdict(list)
    
    for player in batters:
        positions = player.eligible_positions
        
        # Determine primary group
        if any(pos in ['C'] for pos in positions):
            group = "Catchers"
        elif any(pos in ['1B'] for pos in positions):
            group = "First Base"
        elif any(pos in ['2B'] for pos in positions):
            group = "Second Base"
        elif any(pos in ['3B'] for pos in positions):
            group = "Third Base"
        elif any(pos in ['SS'] for pos in positions):
            group = "Shortstop"
        elif any(pos in ['OF', 'LF', 'CF', 'RF'] for pos in positions):
            group = "Outfield"
        elif any(pos in ['DH'] for pos in positions):
            group = "Designated Hitter"
        else:
            group = "Utility"
        
        position_groups[group].append(player)
    
    return dict(position_groups)


def _display_player_cards(players: List[Player], player_type: str) -> None:
    """Display player cards in a grid layout."""
    if not players:
        st.info(f"No {player_type}s found.")
        return
    
    # Display players in rows of 2
    for i in range(0, len(players), 2):
        col1, col2 = st.columns(2)
        
        with col1:
            if i < len(players):
                _display_single_player_card(players[i])
        
        with col2:
            if i + 1 < len(players):
                _display_single_player_card(players[i + 1])


def _display_single_player_card(player: Player) -> None:
    """Display a single player card with detailed information."""
    # Determine card color based on ownership
    if player.percent_owned > 75:
        border_color = "#28a745"  # Green for high ownership
    elif player.percent_owned < 25:
        border_color = "#dc3545"  # Red for low ownership
    else:
        border_color = "#6c757d"  # Gray for medium ownership
    
    # Create card container
    with st.container():
        st.markdown(
            f"""
            <div style="
                border: 2px solid {border_color};
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
                background-color: rgba(255, 255, 255, 0.05);
            ">
            """,
            unsafe_allow_html=True
        )
        
        # Player name and positions
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"**{player.name}**")
            st.caption(f"Positions: {player.display_positions}")
        
        with col2:
            st.markdown(f"**{player.ownership_display}**")
            st.caption("Owned")
        
        # Team and additional info
        if player.mlb_team_name:
            st.markdown(f"🏟️ **Team:** {player.mlb_team_name}")
        
        # Baseball Savant link
        if player.baseball_savant_url:
            st.markdown(f"[📊 Baseball Savant Stats]({player.baseball_savant_url})")
        
        # Player type specific info
        if player.is_pitcher:
            if player.confirmed_start_date:
                st.markdown(f"🗓️ **Next Start:** {player.confirmed_start_date.strftime('%a, %b %d')}")
            
            if player.potential_second_start:
                st.success("🔄 Potential 2nd Start This Week")
        
        st.markdown("</div>", unsafe_allow_html=True)


def _display_roster_insights(players: List[Player]) -> None:
    """Display roster analysis insights."""
    st.subheader("💡 Roster Insights")
    
    insights = []
    
    # Ownership insights
    high_owned = [p for p in players if p.percent_owned > 75]
    low_owned = [p for p in players if p.percent_owned < 25]
    
    if high_owned:
        insights.append(f"⭐ **{len(high_owned)} highly-owned players** (>75% ownership) - likely strong performers")
    
    if low_owned:
        insights.append(f"💎 **{len(low_owned)} low-owned players** (<25% ownership) - potential sleepers or streamers")
    
    # Position balance
    pitchers = [p for p in players if p.is_pitcher]
    batters = [p for p in players if not p.is_pitcher]
    
    pitcher_ratio = len(pitchers) / len(players) * 100 if players else 0
    
    if pitcher_ratio > 60:
        insights.append("⚾ **Pitcher-heavy roster** - consider adding more position players")
    elif pitcher_ratio < 40:
        insights.append("🏏 **Batter-heavy roster** - consider adding more pitchers")
    else:
        insights.append("⚖️ **Well-balanced roster** - good mix of pitchers and batters")
    
    # Upcoming starts for pitchers
    upcoming_starts = [p for p in pitchers if p.confirmed_start_date]
    if upcoming_starts:
        insights.append(f"🗓️ **{len(upcoming_starts)} pitchers** have confirmed upcoming starts")
    
    # Potential second starts
    second_starts = [p for p in pitchers if p.potential_second_start]
    if second_starts:
        insights.append(f"🔄 **{len(second_starts)} pitchers** have potential for second starts this week")
    
    # Display insights
    if insights:
        for insight in insights:
            st.markdown(f"• {insight}")
    else:
        st.info("No specific insights available for your roster.")
    
    # Roster optimization suggestions
    with st.expander("🎯 Roster Optimization Tips", expanded=False):
        st.markdown("""
        **General Tips:**
        - Monitor low-owned players for breakout potential
        - Consider streaming pitchers for favorable matchups
        - Balance roster between proven performers and upside plays
        - Keep an eye on players with upcoming favorable schedules
        
        **For Monday/Tuesday Analysis:**
        - Check the Analysis tab for streaming pitcher options
        - Look for pitchers with potential second starts
        - Consider dropping low-performing players for better matchups
        """)


def _show_roster_placeholder() -> None:
    """Show placeholder content when no roster has been loaded."""
    st.info("""
    👥 **Ready to view your team roster!**
    
    Click the "Refresh Roster" button above to:
    - Load your complete fantasy baseball roster
    - View player details and ownership percentages
    - See organized position groups
    - Get roster analysis insights
    
    Your roster will be displayed with professional player cards showing all relevant information.
    """)
    
    # Show example of what the roster will look like
    with st.expander("📋 Preview: What you'll see", expanded=False):
        st.markdown("""
        **Roster Summary:**
        - Total players, pitchers, and batters count
        - Average ownership percentage
        - High and low owned player counts
        
        **Pitchers Section:**
        - Starting pitchers and relief pitchers
        - Confirmed upcoming starts
        - Potential second start opportunities
        
        **Position Players Section:**
        - Organized by position groups
        - Player cards with team and stats links
        - Ownership percentages and insights
        
        **Roster Insights:**
        - Ownership analysis and recommendations
        - Position balance assessment
        - Optimization suggestions
        """)


def _clear_roster_cache() -> None:
    """Clear roster cache and session state."""
    # Clear session state
    keys_to_clear = ['roster_data', 'refresh_roster']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    # Clear any cached data
    st.cache_data.clear()