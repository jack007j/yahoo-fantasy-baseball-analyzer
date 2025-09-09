"""
Yahoo Fantasy Baseball Streamlit Application

Main entry point for the Streamlit Cloud deployment.
This file must be at the root level for Streamlit Cloud to recognize it.
"""

import streamlit as st
from src.ui.pages.analysis_tab import render_analysis_tab
from src.ui.pages.roster_tab import render_roster_tab
from src.ui.components.sidebar import render_sidebar
from src.ui.components.styling import apply_custom_css, create_section_header
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
    
    # Apply custom styling
    apply_custom_css()
    inject_loading_css()
    
    # Application header with enhanced styling
    st.markdown("""
    <div class="main-header fade-in">
        <h1 style="margin: 0; font-size: 2.5rem;">⚾ Yahoo Fantasy Baseball Analyzer</h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9;">
            Find the best Monday/Tuesday starting pitchers for your fantasy team
        </p>
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
    
    # Sidebar configuration
    with st.sidebar:
        sidebar_config = render_sidebar()
    
    # Show configuration status
    if not sidebar_config.get('is_configured', False):
        st.markdown(create_section_header(
            "🚀 Welcome to Yahoo Fantasy Baseball Analyzer",
            "Configure your team settings in the sidebar to get started"
        ), unsafe_allow_html=True)
        
        # Feature showcase
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="content-section fade-in">
                <h4>📊 Smart Analysis</h4>
                <p>Get confirmed Monday/Tuesday starters with potential second start identification.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="content-section fade-in">
                <h4>🔄 Waiver Wire Intel</h4>
                <p>Compare your roster against available waiver wire options with ownership data.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="content-section fade-in">
                <h4>📈 Advanced Stats</h4>
                <p>Direct links to Baseball Savant for detailed player performance metrics.</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Main application tabs with enhanced styling
    tab1, tab2 = st.tabs(["📊 Analysis", "👥 Roster"])
    
    with tab1:
        render_analysis_tab()
    
    with tab2:
        render_roster_tab()
    
    # Enhanced footer
    st.markdown("---")
    st.markdown("""
    <div class="content-section" style="text-align: center; margin-top: 2rem;">
        <h4>Yahoo Fantasy Baseball Analyzer</h4>
        <p style="margin: 0.5rem 0;">
            <a href='https://github.com/yourusername/yahoo-fantasy-baseball-streamlit' target='_blank' style="text-decoration: none;">
                📚 Documentation
            </a> |
            <a href='https://github.com/yourusername/yahoo-fantasy-baseball-streamlit/issues' target='_blank' style="text-decoration: none;">
                🐛 Report Issues
            </a> |
            <a href='https://fantasy.yahoo.com' target='_blank' style="text-decoration: none;">
                🏟️ Yahoo Fantasy
            </a>
        </p>
        <p style="font-size: 0.85rem; color: #666; margin: 1rem 0 0 0;">
            Data powered by Yahoo Fantasy API & MLB Stats API |
            Built with ❤️ using Streamlit
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()