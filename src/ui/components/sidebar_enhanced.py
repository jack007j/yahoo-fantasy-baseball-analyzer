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
    """Enhanced team ID input with multiple discovery methods."""
    st.sidebar.subheader("⚾ Team Configuration")
    
    # Tab selection for different input methods
    input_method = st.sidebar.radio(
        "Choose input method:",
        ["Direct Entry", "Paste URL", "Mobile Guide"],
        help="Select how you'd like to enter your team information"
    )
    
    team_key = None
    
    if input_method == "Direct Entry":
        # Traditional team key input
        team_key = st.sidebar.text_input(
            "Yahoo Fantasy Team Key",
            value=st.session_state.get('team_key', ''),
            placeholder="e.g., 458.l.135626.t.6",
            help="Enter your team key directly if you know it"
        )
        
        if team_key:
            if _validate_team_key_format(team_key):
                st.sidebar.success("✅ Valid team key format")
                st.session_state['team_key'] = team_key
            else:
                st.sidebar.error("❌ Invalid format")
                st.sidebar.info("Expected: XXX.l.XXXXXX.t.X")
                team_key = None
                
    elif input_method == "Paste URL":
        # URL extraction method - mobile friendly
        st.sidebar.markdown("**📱 Mobile-Friendly Method**")
        st.sidebar.info("Copy any Yahoo Fantasy URL containing your team")
        
        pasted_url = st.sidebar.text_area(
            "Paste Yahoo Fantasy URL:",
            value=st.session_state.get('pasted_url', ''),
            placeholder="https://baseball.fantasysports.yahoo.com/b1/458.l.135626.t.6",
            height=80,
            help="Paste the URL from your browser or mobile app share"
        )
        
        if pasted_url:
            extracted_key = _extract_team_key_from_url(pasted_url)
            if extracted_key:
                st.sidebar.success(f"✅ Found team key: **{extracted_key}**")
                st.session_state['team_key'] = extracted_key
                st.session_state['pasted_url'] = pasted_url
                team_key = extracted_key
                
                # Offer to save for direct entry
                if st.sidebar.button("Use this team key", type="primary"):
                    st.session_state['saved_team_key'] = extracted_key
                    st.sidebar.success("Team key saved!")
            else:
                st.sidebar.error("❌ No valid team key found in URL")
                st.sidebar.caption("Make sure the URL is from your team page")
                
    else:  # Mobile Guide
        _render_mobile_guide()
        
        # Still allow input after reading guide
        st.sidebar.markdown("---")
        st.sidebar.markdown("**After finding your team info:**")
        guide_input = st.sidebar.text_input(
            "Enter Team Key:",
            value=st.session_state.get('team_key', ''),
            placeholder="458.l.135626.t.6"
        )
        
        if guide_input:
            if _validate_team_key_format(guide_input):
                st.sidebar.success("✅ Valid team key")
                st.session_state['team_key'] = guide_input
                team_key = guide_input
            else:
                st.sidebar.error("❌ Invalid format")
    
    # Show current team key if set
    if st.session_state.get('team_key'):
        st.sidebar.markdown("---")
        st.sidebar.info(f"**Current Team:** {st.session_state.get('team_key')}")
        if st.sidebar.button("Clear Team Key"):
            st.session_state.pop('team_key', None)
            st.session_state.pop('pasted_url', None)
            st.rerun()
    
    return team_key


def _render_mobile_guide() -> None:
    """Render mobile-specific guidance for finding team ID."""
    st.sidebar.markdown("""
    ### 📱 Mobile App Instructions
    
    **Yahoo Fantasy Sports App:**
    
    1. **Open the App**
       - Launch Yahoo Fantasy Sports
       - Sign in if needed
    
    2. **Find Your League**
       - Tap the baseball icon
       - Select your league from the list
    
    3. **Get Team Info** (Choose one):
       
       **Option A: Share Method**
       - Tap the share icon (square with arrow)
       - Select "Copy Link"
       - Return here and use "Paste URL" method
       
       **Option B: League Settings**
       - Tap "League" tab
       - Go to "Settings"
       - Find "League ID" (the numbers after 'l.')
       - Note your team number (1-12 typically)
       - Format: `458.l.[league_id].t.[team_number]`
       
       **Option C: Mobile Browser**
       - Open browser on your phone
       - Go to fantasy.yahoo.com
       - Request "Desktop Site" in browser menu
       - Sign in and go to your team
       - Copy URL from address bar
    
    ### 🎯 Quick Tips:
    - Team key format: `XXX.l.XXXXXX.t.X`
    - First number (XXX) = Game code (458 for 2025 MLB)
    - Middle number = Your league ID
    - Last number = Your team number in league
    """)


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
    
    # Ownership threshold with better mobile UX
    ownership_threshold = st.sidebar.select_slider(
        "Min Ownership %",
        options=[0, 10, 25, 50, 75, 90],
        value=0,
        help="Filter by ownership"
    )
    
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
        'ownership_threshold': ownership_threshold,
        'include_second_starts': include_second_starts,
        'show_waiver_players': show_waiver_players
    }


def _render_enhanced_user_guidance() -> None:
    """Render enhanced user guidance with mobile focus."""
    with st.sidebar.expander("❓ Help & Tips", expanded=False):
        tab1, tab2, tab3 = st.tabs(["Desktop", "Mobile", "Tips"])
        
        with tab1:
            st.markdown("""
            **Desktop Browser:**
            1. Go to [fantasy.yahoo.com](https://fantasy.yahoo.com)
            2. Sign in and open your league
            3. Click "My Team"
            4. Copy the URL from address bar
            5. Use "Paste URL" method above
            
            **Example URL:**
            ```
            baseball.fantasysports.yahoo.com/b1/458.l.135626.t.6
            ```
            """)
        
        with tab2:
            st.markdown("""
            **Mobile Options:**
            
            📱 **App Share:**
            - Open Yahoo Fantasy app
            - Go to your team
            - Tap share icon
            - Copy link
            - Paste here
            
            🌐 **Mobile Browser:**
            - Open browser
            - Go to fantasy.yahoo.com
            - Request desktop site
            - Copy URL
            
            ⚙️ **League Settings:**
            - App → League → Settings
            - Find League ID
            - Note your team #
            """)
        
        with tab3:
            st.markdown("""
            **Pro Tips:**
            
            ✅ **Save Time:**
            - Bookmark your team page
            - Save team key in notes
            
            🎯 **Team Key Parts:**
            - `458` = 2025 MLB
            - `l.XXXXX` = League ID
            - `t.X` = Team number
            
            🔄 **Multiple Teams:**
            - Each team has unique key
            - Switch teams by changing key
            """)
    
    with st.sidebar.expander("🔧 Troubleshooting", expanded=False):
        st.markdown("""
        **Common Issues:**
        
        📱 **Mobile Problems:**
        - Can't find team key? Use share function
        - App not working? Try mobile browser
        - URL too long? Copy in parts
        
        ❌ **Invalid Format:**
        - Must have all dots and numbers
        - No spaces or extra characters
        - Format: `XXX.l.XXXXXX.t.X`
        
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