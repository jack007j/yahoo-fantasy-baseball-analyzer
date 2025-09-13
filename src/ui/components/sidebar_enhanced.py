"""
Enhanced sidebar component with mobile-friendly team ID discovery.

Provides multiple methods for finding team IDs, including URL extraction
and mobile app guidance, with improved UX for all devices.
"""

import streamlit as st
from typing import Optional, Dict, Any
import re


def render_enhanced_sidebar() -> Dict[str, Any]:
    """
    Render enhanced sidebar with mobile-optimized team configuration.
    
    Returns:
        Dictionary containing sidebar state and configuration
    """
    st.sidebar.title("⚙️ Configuration")
    
    # Enhanced team ID input section with multiple methods
    team_key = _render_enhanced_team_id_section()
    
    # Analysis settings
    analysis_settings = _render_analysis_settings()
    
    # Enhanced user guidance with mobile focus
    _render_enhanced_user_guidance()
    
    # About section
    _render_about_section()
    
    return {
        'team_key': team_key,
        'analysis_settings': analysis_settings,
        'is_configured': bool(team_key)
    }


def _render_enhanced_team_id_section() -> Optional[str]:
    """Enhanced team ID input with league ID and team selection."""
    st.sidebar.subheader("⚾ Team Configuration")

    # Step 1: League ID input
    st.sidebar.markdown("**Step 1: Enter Your League ID**")
    league_id_input = st.sidebar.text_input(
        "League ID",
        value=st.session_state.get('league_id', ''),
        placeholder="e.g., 135626",
        help="Just the number from your league URL or settings"
    )

    # Build the full league key with game code
    team_key = None

    if league_id_input:
        # Store the league ID
        st.session_state['league_id'] = league_id_input

        # Build the full league key (458 is the 2025 MLB game code)
        from datetime import date
        current_year = date.today().year
        game_code = "458" if current_year == 2025 else "433"  # 433 was 2024
        full_league_key = f"{game_code}.l.{league_id_input}"

        # Step 2: Team selection
        st.sidebar.markdown("**Step 2: Select Your Team**")

        # Try to fetch teams from the league
        try:
            from ...api.yahoo_client import YahooFantasyClient
            client = YahooFantasyClient()

            if client.is_configured():
                # Get teams from the league
                teams_dict = client.get_league_teams(full_league_key)

                if teams_dict:
                    # Create dropdown with team names
                    team_options = ["Select your team..."] + [f"{name}" for name in teams_dict.values()]
                    team_keys_list = [""] + list(teams_dict.keys())

                    # Get the index of the currently selected team if any
                    selected_index = 0
                    if 'selected_team_key' in st.session_state:
                        try:
                            selected_index = team_keys_list.index(st.session_state['selected_team_key'])
                        except ValueError:
                            pass

                    selected_team = st.sidebar.selectbox(
                        "Your Team",
                        options=team_options,
                        index=selected_index,
                        help="Choose your team from the dropdown"
                    )

                    if selected_team != "Select your team...":
                        # Find the team key for the selected team name
                        selected_idx = team_options.index(selected_team)
                        team_key = team_keys_list[selected_idx]
                        st.session_state['team_key'] = team_key
                        st.session_state['selected_team_key'] = team_key
                        st.sidebar.success(f"✅ Team selected: **{selected_team}**")
                else:
                    st.sidebar.warning("No teams found in this league")
            else:
                st.sidebar.error("Yahoo API not configured. Check your OAuth settings.")

        except Exception as e:
            # Fallback to manual entry if API fails
            st.sidebar.warning(f"Could not load teams automatically")
            st.sidebar.markdown("**Manual Team Entry:**")

            team_number = st.sidebar.text_input(
                "Team Number",
                value=st.session_state.get('team_number', ''),
                placeholder="e.g., 6",
                help="Your team number in the league (usually 1-12)"
            )

            if team_number:
                # Build the full team key
                team_key = f"{full_league_key}.t.{team_number}"
                st.session_state['team_key'] = team_key
                st.session_state['team_number'] = team_number
                st.sidebar.success(f"✅ Team key: **{team_key}**")

    # Alternative: Quick paste method
    with st.sidebar.expander("Alternative: Paste URL"):
        st.markdown("**📱 Quick Method**")
        pasted_url = st.text_area(
            "Paste Yahoo Fantasy URL:",
            value=st.session_state.get('pasted_url', ''),
            placeholder="https://baseball.fantasysports.yahoo.com/...",
            height=60,
            help="Paste any URL from your team page"
        )

        if pasted_url:
            extracted_key = _extract_team_key_from_url(pasted_url)
            if extracted_key:
                st.success(f"✅ Found: **{extracted_key}**")
                st.session_state['team_key'] = extracted_key
                st.session_state['pasted_url'] = pasted_url
                team_key = extracted_key

                # Extract league ID from team key
                import re
                match = re.search(r'\.l\.(\d+)\.', extracted_key)
                if match:
                    st.session_state['league_id'] = match.group(1)

    # Show current configuration
    if st.session_state.get('team_key'):
        st.sidebar.markdown("---")
        st.sidebar.info(f"**Active Team:** {st.session_state.get('team_key')}")
        if st.sidebar.button("Clear Configuration"):
            for key in ['team_key', 'league_id', 'selected_team_key', 'team_number', 'pasted_url']:
                st.session_state.pop(key, None)
            st.rerun()

    return team_key




def _extract_team_key_from_url(url: str) -> Optional[str]:
    """
    Extract team key from various Yahoo Fantasy URL formats.
    
    Handles:
    - Desktop URLs: https://baseball.fantasysports.yahoo.com/b1/458.l.135626.t.6
    - Mobile URLs: https://sports.yahoo.com/fantasy/baseball/b1/458.l.135626.t.6
    - App share URLs: Various formats
    
    Args:
        url: Yahoo Fantasy URL
        
    Returns:
        Extracted team key or None if not found
    """
    if not url:
        return None
    
    # Clean the URL
    url = url.strip()
    
    # Pattern for team key: digits.l.digits.t.digits
    patterns = [
        r'(\d+\.l\.\d+\.t\.\d+)',  # Direct pattern
        r'/b\d+/(\d+\.l\.\d+\.t\.\d+)',  # With game prefix
        r'league/(\d+)/team/(\d+)',  # Alternative format
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            if len(match.groups()) == 2:
                # Alternative format - construct team key
                league_id = match.group(1)
                team_id = match.group(2)
                # Assume 2025 MLB game code (458)
                return f"458.l.{league_id}.t.{team_id}"
            else:
                return match.group(1)
    
    return None


def _validate_team_key_format(team_key: str) -> bool:
    """
    Validate Yahoo Fantasy team key format.
    
    Expected format: XXX.l.XXXXXX.t.X
    Example: 458.l.135626.t.6
    
    Args:
        team_key: Team key string to validate
        
    Returns:
        True if format is valid, False otherwise
    """
    if not team_key:
        return False
    
    # Pattern: digits.l.digits.t.digits
    pattern = r'^\d+\.l\.\d+\.t\.\d+$'
    return bool(re.match(pattern, team_key.strip()))


def _render_analysis_settings() -> Dict[str, Any]:
    """Render analysis configuration settings."""
    st.sidebar.subheader("📊 Analysis Settings")

    # Mobile-friendly controls
    col1, col2 = st.sidebar.columns(2)

    with col1:
        # Target days with better mobile layout
        target_days = st.sidebar.multiselect(
            "Target Days",
            options=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            default=["Mon", "Tue"],
            help="Days to analyze"
        )

        # Map short names back to full names
        day_map = {
            "Mon": "Monday", "Tue": "Tuesday", "Wed": "Wednesday",
            "Thu": "Thursday", "Fri": "Friday", "Sat": "Saturday", "Sun": "Sunday"
        }
        target_days = [day_map.get(d, d) for d in target_days]

    # Simplified checkboxes
    col1, col2 = st.sidebar.columns(2)

    with col1:
        include_second_starts = st.sidebar.checkbox(
            "2nd Starts",
            value=True,
            help="Check for second starts"
        )

    with col2:
        show_waiver_players = st.sidebar.checkbox(
            "Waiver Wire",
            value=True,
            help="Include waiver players"
        )

    return {
        'target_days': target_days,
        'ownership_threshold': 0,  # Set to 0 since we removed the slider
        'include_second_starts': include_second_starts,
        'show_waiver_players': show_waiver_players
    }


def _render_enhanced_user_guidance() -> None:
    """Render enhanced user guidance with mobile focus."""
    with st.sidebar.expander("❓ Help & Tips", expanded=False):
        tab1, tab2, tab3 = st.tabs(["Finding League ID", "Mobile", "Tips"])

        with tab1:
            st.markdown("""
            **How to Find Your League ID:**

            🖥️ **Desktop Browser:**
            1. Go to [fantasy.yahoo.com](https://fantasy.yahoo.com)
            2. Sign in and open your league
            3. Look at the URL - find the numbers after "l."

            **Example:**
            ```
            URL: baseball.fantasysports.yahoo.com/b1/458.l.135626.t.6
            League ID: 135626
            ```

            That's it! Just enter **135626** above.
            """)

        with tab2:
            st.markdown("""
            **Mobile Options:**

            📱 **Yahoo Fantasy App:**
            1. Open the app
            2. Go to your league
            3. Tap "League" tab
            4. Select "Settings"
            5. Find "League ID"

            **OR**

            📱 **Mobile Browser:**
            1. Open browser
            2. Go to fantasy.yahoo.com
            3. Request "Desktop Site"
            4. Find league ID in URL
            """)

        with tab3:
            st.markdown("""
            **Pro Tips:**

            ✅ **Simplified Setup:**
            - You only need the league ID number
            - We'll show all teams for you to choose
            - No need to find complex team keys!

            🎯 **What You Need:**
            - Just the 6-digit league ID
            - Example: `135626`
            - That's it!

            🔄 **Multiple Leagues:**
            - Save different league IDs
            - Switch leagues easily
            - Pick your team from dropdown
            """)
    
    with st.sidebar.expander("🔧 Troubleshooting", expanded=False):
        st.markdown("""
        **Common Issues:**

        📱 **Can't Find League ID?**
        - Check League Settings in app
        - Look in any Yahoo Fantasy URL
        - Numbers after "l." are your league ID

        ❌ **Teams Not Loading?**
        - Verify Yahoo OAuth is configured
        - Check that league ID is correct
        - Try the manual team number entry

        🔌 **Connection Issues:**
        - Check internet connection
        - Try refreshing the page
        - Clear browser cache
        
        📊 **No Data:**
        - Verify correct season
        - Check roster has players
        - Ensure league is active
        """)


def _render_about_section() -> None:
    """Render about section with app information."""
    with st.sidebar.expander("ℹ️ About", expanded=False):
        st.markdown("""
        **Yahoo Fantasy Baseball Analyzer**
        
        🎯 **Features:**
        - Find Monday/Tuesday starters
        - Identify second starts
        - Compare waiver options
        - Baseball Savant links
        
        📱 **Mobile Optimized:**
        - Touch-friendly interface
        - Dark mode support
        - Responsive design
        
        🔒 **Privacy:**
        - No data stored
        - Secure API access
        - Real-time analysis
        
        **Version:** 2.0.0
        **Updated:** January 2025
        """)


def get_sidebar_state() -> Dict[str, Any]:
    """Get current sidebar configuration state."""
    return {
        'team_key': st.session_state.get('team_key'),
        'is_configured': bool(st.session_state.get('team_key')),
        'analysis_settings': {
            'target_days': st.session_state.get('target_days', ['Monday', 'Tuesday']),
            'ownership_threshold': st.session_state.get('ownership_threshold', 0),
            'include_second_starts': st.session_state.get('include_second_starts', True),
            'show_waiver_players': st.session_state.get('show_waiver_players', True)
        }
    }