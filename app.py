"""
Yahoo Fantasy Baseball Streamlit Application

Main entry point for the Streamlit Cloud deployment.
This file must be at the root level for Streamlit Cloud to recognize it.
"""

import streamlit as st
from src.ui.pages.analysis_tab_enhanced import render_enhanced_analysis_tab
from src.ui.pages.roster_tab_enhanced import render_enhanced_roster_tab
from src.ui.components.styling_enhanced import apply_enhanced_css
from src.ui.components.styling import create_section_header
from src.ui.components.loading import inject_loading_css
from src.core.config import get_config


def main() -> None:
    """Main application entry point."""
    # Configure Streamlit page
    st.set_page_config(
        page_title="Yahoo Fantasy Baseball Analyzer",
        page_icon="⚾",
        layout="wide",
        initial_sidebar_state="collapsed",
        menu_items={
            'Get Help': 'https://github.com/yourusername/yahoo-fantasy-baseball-streamlit',
            'Report a bug': 'https://github.com/yourusername/yahoo-fantasy-baseball-streamlit/issues',
            'About': """
            # Yahoo Fantasy Baseball Analyzer
            
            Analyze your Yahoo Fantasy Baseball league for optimal Monday/Tuesday starter pickups.
            
            **Features:**
            - Find confirmed probable starters for Monday/Tuesday
            - Identify potential second starts
            - Compare waiver wire vs. roster options
            - Direct links to Baseball Savant player pages
            
            Built with Streamlit and powered by Yahoo Fantasy API and MLB Stats API.
            """
        }
    )
    
    # Apply enhanced styling with dark mode and mobile support
    apply_enhanced_css()
    inject_loading_css()
    
    # Enhanced dark header with subtle effects and tab styling
    st.markdown("""
        <style>
        .app-header {
            background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
            padding: 16px 12px;
            margin: -3rem -1rem 1rem -1rem;
            border-bottom: 3px solid #ff4444;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            position: relative;
            overflow: hidden;
        }

        .app-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.03), transparent);
            animation: shimmer 8s infinite;
        }

        @keyframes shimmer {
            0% { left: -100%; }
            100% { left: 100%; }
        }

        .app-title {
            color: #ffffff;
            font-size: 32px;
            font-weight: 600;
            text-align: center;
            margin: 0;
            letter-spacing: -0.5px;
            position: relative;
            z-index: 1;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }

        .app-desc {
            color: #a0a0a0;
            font-size: 16px;
            text-align: center;
            margin: 8px 0 0 0;
            position: relative;
            z-index: 1;
            font-weight: 400;
            letter-spacing: 0.3px;
        }

        /* Main Analysis/Roster tab styling */
        div[data-testid="stHorizontalBlock"] > div:has(> div[data-baseweb="tab-list"]) {
            background-color: #1a1a1a;
            padding: 1px;
            border-radius: 6px;
            margin-top: 1rem;
            margin-bottom: 1rem;
            border-bottom: 2px solid #ff4444;
        }

        .stTabs [data-baseweb="tab"] {
            color: #999;
            background: transparent;
            font-weight: 500;
            font-size: 14px;
            border: none;
            padding: 8px 20px;
            margin: 0 2px;
            transition: all 0.2s ease;
            border-radius: 4px;
        }

        .stTabs [data-baseweb="tab"]:hover {
            color: #fff;
            background: rgba(255, 255, 255, 0.1);
        }

        .stTabs [aria-selected="true"] {
            background: #8b0000 !important;
            color: white !important;
            font-weight: 600;
        }

        /* Remove ALL top spacing */
        .main .block-container {
            padding-top: 0 !important;
            max-width: 100%;
        }

        .stApp > header {
            display: none !important;
        }

        .stHeader {
            margin-top: 0 !important;
            margin-bottom: 0.25rem !important;
            padding-top: 0 !important;
        }

        div[data-testid="stVerticalBlock"] {
            gap: 0.5rem !important;
        }

        @media (max-width: 600px) {
            .app-title {
                font-size: 24px;
            }
            .app-desc {
                font-size: 14px;
            }
            .stTabs [data-baseweb="tab"] {
                font-size: 14px;
                padding: 8px 16px;
            }
        }
        </style>

        <div class="app-header">
            <div class="app-title">Yahoo Baseball Pitcher Streamer</div>
            <div class="app-desc">Find two-start starting pitchers on your waiver wire</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Initialize configuration
    try:
        config = get_config()
    except Exception as e:
        st.error(f"⚠️ Configuration error: {str(e)}")
        st.info("""
        **Troubleshooting:**
        - Check your environment variables
        - Ensure all required dependencies are installed
        - Verify your Yahoo API credentials are configured
        """)
        st.stop()

    # Configuration section (mobile-friendly, no sidebar)
    # Step 1: League ID input
    col1, col2 = st.columns([4, 1])

    with col1:
        league_id = st.text_input(
            "League ID",
            value=st.session_state.get('league_id', ''),
            placeholder="e.g., 135626",
            help="Your Yahoo Fantasy Baseball league ID",
            key="input_league_id"
        )

    with col2:
        st.markdown("<div style='height: 1px'></div>", unsafe_allow_html=True)
        fetch_teams = st.button("Load League Teams", type="primary", use_container_width=True)

    # Step 2: Team selection (only shown after league ID is entered)
    if fetch_teams and league_id:
        st.session_state['league_id'] = league_id
        st.session_state['fetch_teams'] = True
        st.rerun()

    # Try to load teams if league ID is set
    if st.session_state.get('league_id') and st.session_state.get('fetch_teams', False):
        try:
            from src.api.yahoo_client import YahooFantasyClient

            with st.spinner("Loading teams..."):
                client = YahooFantasyClient()
                if client.is_configured():
                    full_league_key = f"458.l.{st.session_state['league_id']}"
                    teams_dict = client.get_league_teams(full_league_key)

                    if teams_dict:
                        st.session_state['teams_dict'] = teams_dict
                        st.session_state['teams_loaded'] = True
                    else:
                        st.warning("No teams found in this league")
                else:
                    st.error("Yahoo API not configured")
        except Exception as e:
            # Fallback to manual entry
            st.session_state['manual_entry'] = True
            st.warning(f"Could not load teams: {str(e)[:100]}")

    # Show team selector if teams are loaded
    if st.session_state.get('teams_loaded') and st.session_state.get('teams_dict'):
        teams_dict = st.session_state['teams_dict']
        team_options = ["Select your team..."] + list(teams_dict.values())

        selected_team = st.selectbox(
            "Your Team",
            options=team_options,
            key="team_selector"
        )

        if selected_team and selected_team != "Select your team...":
            # Find the team key for the selected team
            for key, name in teams_dict.items():
                if name == selected_team:
                    team_key = key
                    # Extract team number from key (e.g., "458.l.135626.t.6" -> "6")
                    team_number = team_key.split('.t.')[-1]

                    st.session_state['team_key'] = team_key
                    st.session_state['team_number'] = team_number
                    st.session_state['configured'] = True
                    break

    # Fallback: Manual team number entry (only if API fails)
    elif st.session_state.get('manual_entry') or (st.session_state.get('league_id') and not st.session_state.get('teams_loaded')):
        team_number = st.text_input(
            "Team Number (manual entry)",
            value=st.session_state.get('team_number', ''),
            placeholder="e.g., 6",
            help="Enter your team number manually",
            key="manual_team_number"
        )

        if team_number:
            full_league_key = f"458.l.{st.session_state['league_id']}"
            team_key = f"{full_league_key}.t.{team_number}"

            st.session_state['team_key'] = team_key
            st.session_state['team_number'] = team_number
            st.session_state['configured'] = True

    # Help expander (collapsed by default)
    with st.expander("📖 Help & Tips", expanded=False):
        col_help1, col_help2 = st.columns(2)

        with col_help1:
            st.markdown("""
            **🔍 Finding Your League ID:**
            1. Go to your Yahoo Fantasy league
            2. Check the URL: `.../b1/135626`
            3. The number (135626) is your League ID
            """)

        with col_help2:
            st.markdown("""
            **🔢 Finding Your Team Number:**
            - Check your team URL: `.../t.6`
            - Or count your position in standings
            - Team 1, Team 2, etc.
            """)

    # Minimal spacing after help section
    st.markdown("<div style='height: 1px'></div>", unsafe_allow_html=True)

    # Check if configured
    is_configured = st.session_state.get('configured', False)
        

    
    # Main application tabs with enhanced styling
    tab1, tab2 = st.tabs(["Analysis", "Roster"])
    
    with tab1:
        render_enhanced_analysis_tab()
    
    with tab2:
        render_enhanced_roster_tab()
    


if __name__ == "__main__":
    main()