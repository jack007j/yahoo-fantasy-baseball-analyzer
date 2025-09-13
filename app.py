"""
Yahoo Fantasy Baseball Streamlit Application

Main entry point for the Streamlit Cloud deployment.
This file must be at the root level for Streamlit Cloud to recognize it.
"""

import streamlit as st
from src.ui.pages.analysis_tab_enhanced import render_enhanced_analysis_tab
from src.ui.pages.roster_tab_enhanced import render_enhanced_roster_tab
from src.ui.components.sidebar_enhanced import render_enhanced_sidebar
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
        initial_sidebar_state="expanded",
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
            padding: 4px;
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
    
    # Enhanced sidebar with mobile-friendly team ID discovery
    with st.sidebar:
        sidebar_config = render_enhanced_sidebar()
    
    # Show configuration status
    if not sidebar_config.get('is_configured', False):
        st.info("🔧 Configure your team key in the sidebar")
        

    
    # Main application tabs with enhanced styling
    tab1, tab2 = st.tabs(["Analysis", "Roster"])
    
    with tab1:
        render_enhanced_analysis_tab()
    
    with tab2:
        render_enhanced_roster_tab()
    


if __name__ == "__main__":
    main()