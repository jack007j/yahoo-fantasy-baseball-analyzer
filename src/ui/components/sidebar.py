"""
Sidebar component for Yahoo Fantasy Baseball Streamlit application.

Provides team ID input, configuration options, and user guidance.
"""

import streamlit as st
from typing import Optional, Dict, Any
import re

from ...core.config import AppConfig
from ...core.exceptions import DataValidationError


def render_sidebar() -> Dict[str, Any]:
    """
    Render the sidebar with team configuration and guidance.
    
    Returns:
        Dictionary containing sidebar state and configuration
    """
    st.sidebar.title("⚙️ Configuration")
    
    # Team ID input section
    team_key = _render_team_id_section()
    
    # Analysis settings
    analysis_settings = _render_analysis_settings()
    
    # User guidance
    _render_user_guidance()
    
    # About section
    _render_about_section()
    
    return {
        'team_key': team_key,
        'analysis_settings': analysis_settings,
        'is_configured': bool(team_key)
    }


def _render_team_id_section() -> Optional[str]:
    """Render team ID input section with validation and guidance."""
    st.sidebar.subheader("🏈 Team Configuration")
    
    # Team ID input
    team_key = st.sidebar.text_input(
        "Yahoo Fantasy Team Key",
        value=st.session_state.get('team_key', ''),
        placeholder="e.g., 458.l.135626.t.6",
        help="Enter your Yahoo Fantasy Baseball team key. See guidance below for help finding it."
    )
    
    # Validate team key format
    if team_key:
        if _validate_team_key_format(team_key):
            st.sidebar.success("✅ Valid team key format")
            st.session_state['team_key'] = team_key
            return team_key
        else:
            st.sidebar.error("❌ Invalid team key format")
            st.sidebar.info("Expected format: XXX.l.XXXXXX.t.X")
            return None
    
    return None


def _render_analysis_settings() -> Dict[str, Any]:
    """Render analysis configuration settings."""
    st.sidebar.subheader("📊 Analysis Settings")
    
    # Target days selection
    target_days = st.sidebar.multiselect(
        "Target Days for Analysis",
        options=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        default=["Monday", "Tuesday"],
        help="Select which days to analyze for starting pitchers"
    )
    
    # Ownership threshold
    ownership_threshold = st.sidebar.slider(
        "Minimum Ownership %",
        min_value=0,
        max_value=100,
        value=0,
        step=5,
        help="Filter players below this ownership percentage"
    )
    
    # Include second start analysis
    include_second_starts = st.sidebar.checkbox(
        "Analyze Potential Second Starts",
        value=True,
        help="Check for pitchers who might get a second start in the week"
    )
    
    # Show waiver players
    show_waiver_players = st.sidebar.checkbox(
        "Include Waiver Wire Players",
        value=True,
        help="Include available players from the waiver wire"
    )
    
    return {
        'target_days': target_days,
        'ownership_threshold': ownership_threshold,
        'include_second_starts': include_second_starts,
        'show_waiver_players': show_waiver_players
    }


def _render_user_guidance() -> None:
    """Render expandable user guidance section."""
    with st.sidebar.expander("❓ How to Find Your Team Key", expanded=False):
        st.markdown("""
        **Step-by-step instructions:**
        
        1. **Go to Yahoo Fantasy Baseball**
           - Visit [fantasy.yahoo.com](https://fantasy.yahoo.com)
           - Sign in to your account
        
        2. **Navigate to Your League**
           - Click on your Baseball league
           - Go to "My Team" page
        
        3. **Find Team Key in URL**
           - Look at the browser address bar
           - Find the pattern: `XXX.l.XXXXXX.t.X`
           - Example: `458.l.135626.t.6`
        
        4. **Copy the Complete Team Key**
           - Include all numbers and dots
           - Paste it in the field above
        
        **URL Example:**
        ```
        https://baseball.fantasysports.yahoo.com/b1/458.l.135626.t.6
        ```
        **Team Key:** `458.l.135626.t.6`
        
        **Need Help?**
        - The team key uniquely identifies your team
        - It includes game code, league ID, and team ID
        - Make sure to copy the entire key with dots
        """)
    
    with st.sidebar.expander("🔧 Troubleshooting", expanded=False):
        st.markdown("""
        **Common Issues:**
        
        **Invalid Team Key Format**
        - Ensure format: `XXX.l.XXXXXX.t.X`
        - Include all dots and numbers
        - No spaces or extra characters
        
        **Can't Find Team Key**
        - Make sure you're logged into Yahoo
        - Navigate to "My Team" page
        - Check the URL in your browser
        
        **API Connection Issues**
        - Check your internet connection
        - Yahoo API may be temporarily down
        - Try refreshing the page
        
        **No Data Returned**
        - Verify team key is correct
        - Ensure you have players on your roster
        - Check if it's the current baseball season
        """)


def _render_about_section() -> None:
    """Render about section with app information."""
    with st.sidebar.expander("ℹ️ About This App", expanded=False):
        st.markdown("""
        **Yahoo Fantasy Baseball Analyzer**
        
        This app helps you find the best Monday/Tuesday starting pitchers for your fantasy team by:
        
        - 🎯 **Finding confirmed starters** for target days
        - 🔄 **Identifying potential second starts** in the week
        - 📊 **Comparing ownership percentages** across leagues
        - 🔗 **Providing Baseball Savant links** for detailed stats
        - ⚖️ **Showing waiver vs. roster options** side by side
        
        **Data Sources:**
        - Yahoo Fantasy API for team/league data
        - MLB Stats API for probable pitchers
        - Baseball Savant for advanced statistics
        
        **Privacy:**
        - No data is stored permanently
        - All analysis happens in real-time
        - Your Yahoo credentials stay secure
        """)


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


def show_configuration_status() -> bool:
    """Show configuration status in main area when not configured."""
    # Check Yahoo OAuth configuration
    try:
        from ...api.yahoo_client import YahooFantasyClient
        yahoo_client = YahooFantasyClient()
        
        if not yahoo_client.is_configured():
            st.error("""
            🔐 **Yahoo OAuth Configuration Required**
            
            The Yahoo Fantasy API credentials are not configured. This application requires:
            - Yahoo Developer App credentials (Client ID & Secret)
            - OAuth access tokens for your Yahoo account
            
            Please see the deployment guide for setup instructions.
            """)
            
            with st.expander("🔧 Configuration Setup Guide", expanded=False):
                st.markdown("""
                **Required Steps:**
                
                1. **Create Yahoo Developer App**
                   - Go to [Yahoo Developer Console](https://developer.yahoo.com/apps/)
                   - Create a new app with Fantasy Sports API access
                   - Note your Client ID and Client Secret
                
                2. **Generate OAuth Tokens**
                   - Use the Yahoo OAuth flow to get access/refresh tokens
                   - See the deployment guide for detailed instructions
                
                3. **Configure Streamlit Secrets**
                   - Add credentials to `.streamlit/secrets.toml`
                   - Include: client_id, client_secret, access_token, refresh_token
                
                **For Development:**
                - Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`
                - Fill in your Yahoo OAuth credentials
                
                **For Deployment:**
                - Add secrets in Streamlit Cloud dashboard
                - See deployment guide for security best practices
                """)
            
            return True
    
    except Exception as e:
        st.error(f"❌ Error checking Yahoo configuration: {str(e)}")
        return True
    
    # Check team key configuration
    if not st.session_state.get('team_key'):
        st.warning("""
        🔧 **Team Configuration Required**
        
        Please enter your Yahoo Fantasy team key in the sidebar to get started.
        
        👈 Look for the "Team Configuration" section in the sidebar and follow the guidance to find your team key.
        """)
        
        st.info("""
        **What you'll get once configured:**
        - Analysis of confirmed Monday/Tuesday starters
        - Potential second start identification
        - Waiver wire vs. roster comparisons
        - Direct links to Baseball Savant player pages
        """)
        
        return True
    
    return False


def get_sidebar_state() -> Dict[str, Any]:
    """Get current sidebar configuration state."""
    analysis_settings = {
        'target_days': st.session_state.get('target_days', ['Monday', 'Tuesday']),
        'ownership_threshold': st.session_state.get('ownership_threshold', 0),
        'include_second_starts': st.session_state.get('include_second_starts', True),
        'show_waiver_players': st.session_state.get('show_waiver_players', True)
    }
    
    return {
        'team_key': st.session_state.get('team_key'),
        'is_configured': bool(st.session_state.get('team_key')),
        'analysis_settings': analysis_settings
    }