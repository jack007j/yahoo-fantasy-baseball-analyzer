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
    
    # Compact application header
    st.markdown("""
    <div class="main-header fade-in" style="padding: 0.5rem 0;">
        <h2>Yahoo Fantasy Baseball Analyzer</h2>
        <p style="font-size: 0.9rem;">Find two-start starting pitchers on your waiver wire</p>
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
        st.info("🔧 Configure your team key in the sidebar to get started")
        
        # Compact feature showcase
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.caption("📊 **Analysis**: Mon/Tue starters")
        
        with col2:
            st.caption("🔄 **Waiver**: Available pitchers")
        
        with col3:
            st.caption("📈 **Stats**: Savant links")
    
    # Main application tabs with enhanced styling
    tab1, tab2 = st.tabs(["Analysis", "Roster"])
    
    with tab1:
        render_enhanced_analysis_tab()
    
    with tab2:
        render_enhanced_roster_tab()
    
    # Enhanced footer with dark mode support
    st.markdown("---")
    st.markdown("""
    <div class="content-section" style="text-align: center; margin-top: 2rem;">
        <h4>Yahoo Fantasy Baseball Analyzer</h4>
        <p style="margin: 0.5rem 0;">
            <a href='https://github.com/yourusername/yahoo-fantasy-baseball-streamlit' target='_blank'>
                📚 Documentation
            </a> |
            <a href='https://github.com/yourusername/yahoo-fantasy-baseball-streamlit/issues' target='_blank'>
                🐛 Report Issues
            </a> |
            <a href='https://fantasy.yahoo.com' target='_blank'>
                🏟️ Yahoo Fantasy
            </a>
        </p>
        <p style="font-size: 0.85rem; color: var(--text-muted); margin: 1rem 0 0 0;">
            Data powered by Yahoo Fantasy API & MLB Stats API |
            Built with Streamlit | Dark mode & mobile optimized
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()