"""
Enhanced roster tab with player profile pictures and improved visual design.

Displays user's team roster with player cards, profile images, and Baseball Savant links.
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional
from collections import defaultdict
import requests

from ...models.player import Player
from ...services.analysis_service import AnalysisService
from ...api.yahoo_client import YahooFantasyClient
from ...api.mlb_client import MLBStatsClient
from ...services.cache_service import CacheService
from ...core.exceptions import AnalysisError, APIError
# Removed sidebar import - using session state directly


def render_enhanced_roster_tab() -> None:
    """Render the enhanced roster tab with player cards and images."""
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
    st.markdown("### My Team Roster")

    # Custom styling for pitcher/position tabs
    st.markdown("""
        <style>
        /* Style the pitcher/position player tabs */
        div[data-testid="stVerticalBlock"] > div:has(> div[data-baseweb="tab-list"]) {
            background-color: #1a1a1a;
            padding: 4px;
            border-radius: 6px;
            margin-bottom: 0.75rem;
        }

        /* Tab buttons */
        .stTabs [data-baseweb="tab"] {
            color: #999;
            background: transparent;
            border: none;
            padding: 8px 16px;
            font-weight: 500;
        }

        .stTabs [data-baseweb="tab"]:hover {
            color: #ccc;
        }

        .stTabs [aria-selected="true"] {
            color: #fff !important;
            background: #8b0000 !important;
            border-radius: 4px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Check configuration from session state
    team_key = st.session_state.get('team_key')

    if not team_key:
        st.warning("⚾ Enter your League ID and Select Team above")
        return
    
    # Load roster if needed (auto-load on tab switch)
    if 'roster_data' not in st.session_state:
        _load_enhanced_roster_data(team_key)
    
    # Display roster
    if 'roster_data' in st.session_state:
        _display_enhanced_roster(st.session_state['roster_data'])
    else:
        _show_roster_placeholder()


def _load_enhanced_roster_data(team_key: str) -> None:
    """Load roster data with enhanced player information."""
    try:
        with st.spinner("⚾ Loading your team roster..."):
            # Initialize services
            yahoo_client = YahooFantasyClient()
            mlb_client = MLBStatsClient()
            cache_service = CacheService()
            analysis_service = AnalysisService(yahoo_client, mlb_client, cache_service)
            
            # Get roster data
            roster_players = analysis_service.get_team_roster(team_key)
            
            # Players already have the fields defined, we can optionally set them
            # But they also have properties that compute them if not set
            
            # Store results
            st.session_state['roster_data'] = {
                'players': roster_players,
                'timestamp': pd.Timestamp.now()
            }
            
            st.session_state['load_status'] = 'success'
    
    except Exception as e:
        st.session_state['load_status'] = f"Error: {str(e)}"


# Helper functions removed - now using Player model properties


def _display_enhanced_roster(roster_data: Dict[str, Any]) -> None:
    """Display enhanced roster with player cards and images."""
    players = roster_data['players']
    
    if not players:
        st.warning("No players found on your roster.")
        return
    
    # Group players
    pitchers = [p for p in players if p.is_pitcher]
    batters = [p for p in players if not p.is_pitcher]
    
    # Create tabs for roster sections (removed Stats Overview)
    tab1, tab2 = st.tabs([
        f"Pitchers ({len(pitchers)})", 
        f"Position Players ({len(batters)})"
    ])
    
    with tab1:
        if pitchers:
            _display_enhanced_pitcher_section(pitchers)
        else:
            st.info("No pitchers on your roster")
    
    with tab2:
        if batters:
            _display_enhanced_batter_section(batters)
        else:
            st.info("No position players on your roster")


def _display_enhanced_summary_REMOVED(players: List[Player]) -> None:
    """Display enhanced roster summary with visual metrics."""
    st.subheader("📊 Roster Overview")
    
    # Calculate metrics
    total_players = len(players)
    pitchers = [p for p in players if p.is_pitcher]
    batters = [p for p in players if not p.is_pitcher]
    
    # Create metric columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Players", total_players, help="Total roster size")
    
    with col2:
        st.metric("Pitchers", len(pitchers), f"{len(pitchers)/total_players*100:.0f}% of roster")
    
    with col3:
        st.metric("Batters", len(batters), f"{len(batters)/total_players*100:.0f}% of roster")
    
    with col4:
        # Count players with upcoming starts
        upcoming = len([p for p in pitchers if p.confirmed_start_date])
        st.metric("Upcoming Starts", upcoming, "This week" if upcoming > 0 else None)


def _display_enhanced_pitcher_section(pitchers: List[Player]) -> None:
    """Display pitchers with compact cards."""
    # Group by pitcher type
    starters = [p for p in pitchers if 'SP' in p.eligible_positions]
    relievers = [p for p in pitchers if 'RP' in p.eligible_positions and 'SP' not in p.eligible_positions]
    
    if starters:
        st.markdown(f"**Starting Pitchers** ({len(starters)} players)")
        _display_player_grid(starters, "pitcher")
    
    if relievers:
        st.markdown(f"**Relief Pitchers** ({len(relievers)} players)")
        _display_player_grid(relievers, "pitcher")


def _display_enhanced_batter_section(batters: List[Player]) -> None:
    """Display batters with compact cards."""
    # Group by position
    position_groups = {
        "Infield": [],
        "Outfield": [],
        "Catcher/DH": []
    }
    
    for player in batters:
        positions = player.eligible_positions
        if any(pos in ['C', 'DH'] for pos in positions):
            position_groups["Catcher/DH"].append(player)
        elif any(pos in ['OF', 'LF', 'CF', 'RF'] for pos in positions):
            position_groups["Outfield"].append(player)
        else:
            position_groups["Infield"].append(player)
    
    for group_name, group_players in position_groups.items():
        if group_players:
            st.markdown(f"**{group_name}** ({len(group_players)} players)")
            _display_player_grid(group_players, "batter")


def _display_player_grid(players: List[Player], player_type: str) -> None:
    """Display players in a compact mobile-friendly list."""
    # Display as a vertical list with compact cards
    for player in players:
        _display_enhanced_player_card(player, player_type)


def _display_enhanced_player_card(player: Player, player_type: str) -> None:
    """Display a compact mobile-optimized player card."""
    import urllib.parse
    
    # Build badges for pitchers
    badges = ""
    if player_type == "pitcher" and player.confirmed_start_date:
        badges = f' • 📅 {player.confirmed_start_date.strftime("%a")}'
        if player.potential_second_start:
            badges += ' • 🔄 2nd'
    
    # Build Savant link
    if player.baseball_savant_url:
        savant_link = player.baseball_savant_url
        savant_text = "📊 Savant Profile"
    else:
        search_name = urllib.parse.quote(player.name)
        savant_link = f"https://baseballsavant.mlb.com/player_search?player_search={search_name}"
        savant_text = "🔍 Savant Profile"
    
    # Use HTML with proper flex properties to prevent wrapping
    card_html = f'''
    <div style="display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid #e0e0e0;">
        <img src="{player.get_profile_image_url}" style="height: 40px; border-radius: 6px; flex: 0 0 auto; object-fit: contain;">
        <div style="flex: 1 1 auto; min-width: 0; overflow: hidden;">
            <div style="font-weight: 600; font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{player.name}</div>
            <div style="font-size: 12px; color: #666; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{player.display_positions}{badges}</div>
        </div>
        <a href="{savant_link}" target="_blank" style="background: rgba(0,0,0,0.7); color: white; padding: 8px 12px; border-radius: 6px; text-decoration: none; font-size: 13px; flex: 0 0 auto; white-space: nowrap; display: flex; align-items: center; justify-content: center;">{savant_text}</a>
    </div>
    '''
    
    st.markdown(card_html, unsafe_allow_html=True)


def _display_roster_stats_overview_REMOVED(players: List[Player]) -> None:
    """Display statistical overview of the roster."""
    st.subheader("📈 Roster Statistics")
    
    # Create DataFrame for analysis
    df_data = []
    for player in players:
        df_data.append({
            'Name': player.name,
            'Position': player.display_positions,
            'Ownership %': player.percent_owned,
            'Type': 'Pitcher' if player.is_pitcher else 'Batter'
        })
    
    df = pd.DataFrame(df_data)
    
    # Display summary stats
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Position Distribution")
        position_counts = df['Type'].value_counts()
        st.bar_chart(position_counts)
    
    with col2:
        st.markdown("### Ownership Distribution")
        ownership_bins = pd.cut(df['Ownership %'], 
                               bins=[0, 25, 50, 75, 100],
                               labels=['Low (0-25%)', 'Medium (25-50%)', 
                                      'High (50-75%)', 'Very High (75-100%)'])
        ownership_dist = ownership_bins.value_counts()
        st.bar_chart(ownership_dist)
    
    # Full roster table with sorting
    st.markdown("### Complete Roster Table")
    st.dataframe(
        df.sort_values('Ownership %', ascending=False),
        use_container_width=True,
        hide_index=True,
        column_config={
            'Ownership %': st.column_config.ProgressColumn(
                'Ownership %',
                help='Percentage owned in Yahoo leagues',
                format='%.1f%%',
                min_value=0,
                max_value=100
            )
        }
    )


def _show_roster_placeholder() -> None:
    """Show placeholder when roster hasn't been loaded."""
    st.info("""
    ⚾ **Ready to view your enhanced roster!**
    
    Click the "Refresh" button to load your team with:
    - Player profile pictures
    - Baseball Savant links for every player
    - Upcoming pitcher starts
    - Visual ownership indicators
    - Mobile-optimized card layout
    
    Your roster will be displayed with beautiful player cards showing all relevant information.
    """)
    
    # Show sample card
    with st.expander("👀 Preview: Enhanced Player Cards", expanded=False):
        st.markdown("""
        **Each player card includes:**
        - 📸 Profile picture from MLB
        - ⚾ Name and eligible positions
        - 🏟️ Current MLB team
        - 📊 Direct Baseball Savant link
        - 📈 Ownership percentage (secondary metric)
        - 🗓️ Next start date (for pitchers)
        - 🔄 Second start indicators
        
        **Organized by:**
        - Starting Pitchers
        - Relief Pitchers
        - Infielders
        - Outfielders
        - Catchers/DH
        """)