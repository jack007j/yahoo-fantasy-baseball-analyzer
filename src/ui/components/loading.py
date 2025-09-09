"""
Loading and progress indicator components for Yahoo Fantasy Baseball Streamlit application.

Provides consistent loading states and progress feedback throughout the application.
"""

import streamlit as st
import time
from typing import Optional, List, Dict, Any
from contextlib import contextmanager


class LoadingManager:
    """Manages loading states and progress indicators."""
    
    @staticmethod
    @contextmanager
    def spinner(message: str = "Loading...", success_message: Optional[str] = None):
        """
        Context manager for spinner loading indicator.
        
        Args:
            message: Loading message to display
            success_message: Optional success message to show when complete
        """
        with st.spinner(message):
            try:
                yield
                if success_message:
                    st.success(success_message)
            except Exception as e:
                st.error(f"Error: {str(e)}")
                raise
    
    @staticmethod
    def progress_bar(steps: List[str], current_step: int = 0) -> st.progress:
        """
        Create a progress bar with step labels.
        
        Args:
            steps: List of step descriptions
            current_step: Current step index (0-based)
            
        Returns:
            Streamlit progress bar object
        """
        progress_bar = st.progress(0)
        progress_text = st.empty()
        
        if current_step < len(steps):
            progress_value = (current_step + 1) / len(steps)
            progress_bar.progress(progress_value)
            progress_text.text(f"Step {current_step + 1}/{len(steps)}: {steps[current_step]}")
        
        return progress_bar, progress_text
    
    @staticmethod
    def update_progress(progress_bar, progress_text, steps: List[str], current_step: int):
        """Update progress bar and text."""
        if current_step < len(steps):
            progress_value = (current_step + 1) / len(steps)
            progress_bar.progress(progress_value)
            progress_text.text(f"Step {current_step + 1}/{len(steps)}: {steps[current_step]}")
        elif current_step >= len(steps):
            progress_bar.progress(1.0)
            progress_text.text("✅ Complete!")


def show_analysis_loading() -> None:
    """Show loading state for analysis operations."""
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <div class="loading-spinner"></div>
        <h3>🔍 Analyzing Monday/Tuesday Starters</h3>
        <p>This may take a few moments while we:</p>
        <ul style="text-align: left; display: inline-block;">
            <li>Fetch your team roster from Yahoo Fantasy</li>
            <li>Get waiver wire pitcher data</li>
            <li>Query MLB API for probable starters</li>
            <li>Match players and analyze schedules</li>
            <li>Calculate second start probabilities</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)


def show_roster_loading() -> None:
    """Show loading state for roster operations."""
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <div class="loading-spinner"></div>
        <h3>👥 Loading Your Team Roster</h3>
        <p>Fetching player data and statistics...</p>
    </div>
    """, unsafe_allow_html=True)


def show_api_status(api_name: str, status: str, details: Optional[str] = None) -> None:
    """
    Show API connection status.
    
    Args:
        api_name: Name of the API (e.g., "Yahoo Fantasy", "MLB Stats")
        status: Status ("connected", "error", "loading")
        details: Optional additional details
    """
    if status == "connected":
        st.success(f"✅ {api_name} API - Connected")
    elif status == "error":
        st.error(f"❌ {api_name} API - Connection Error")
        if details:
            st.caption(f"Details: {details}")
    elif status == "loading":
        st.info(f"🔄 {api_name} API - Connecting...")
    else:
        st.warning(f"⚠️ {api_name} API - Unknown Status")


def show_data_freshness(timestamp: Optional[str], cache_duration: int = 300) -> None:
    """
    Show data freshness indicator.
    
    Args:
        timestamp: ISO timestamp of when data was last updated
        cache_duration: Cache duration in seconds
    """
    if not timestamp:
        st.caption("🔄 Data not loaded")
        return
    
    import pandas as pd
    
    try:
        last_update = pd.to_datetime(timestamp)
        now = pd.Timestamp.now()
        age_seconds = (now - last_update).total_seconds()
        
        if age_seconds < 60:
            st.caption(f"🟢 Data fresh (updated {int(age_seconds)}s ago)")
        elif age_seconds < cache_duration:
            st.caption(f"🟡 Data cached (updated {int(age_seconds/60)}m ago)")
        else:
            st.caption(f"🔴 Data stale (updated {int(age_seconds/60)}m ago) - Consider refreshing")
    
    except Exception:
        st.caption("⚠️ Unable to determine data freshness")


def show_operation_status(operation: str, status: str, message: Optional[str] = None) -> None:
    """
    Show operation status with appropriate styling.
    
    Args:
        operation: Name of the operation
        status: Status ("success", "error", "warning", "info")
        message: Optional message to display
    """
    icons = {
        "success": "✅",
        "error": "❌", 
        "warning": "⚠️",
        "info": "ℹ️"
    }
    
    icon = icons.get(status, "•")
    display_message = f"{icon} {operation}"
    
    if message:
        display_message += f": {message}"
    
    if status == "success":
        st.success(display_message)
    elif status == "error":
        st.error(display_message)
    elif status == "warning":
        st.warning(display_message)
    else:
        st.info(display_message)


def show_step_progress(steps: List[Dict[str, Any]], current_step: int = 0) -> None:
    """
    Show step-by-step progress with visual indicators.
    
    Args:
        steps: List of step dictionaries with 'name' and optional 'description'
        current_step: Current step index (0-based)
    """
    st.markdown("### Progress")
    
    for i, step in enumerate(steps):
        if i < current_step:
            # Completed step
            st.markdown(f"✅ **{step['name']}**")
            if step.get('description'):
                st.caption(f"   {step['description']}")
        elif i == current_step:
            # Current step
            st.markdown(f"🔄 **{step['name']}** *(in progress)*")
            if step.get('description'):
                st.caption(f"   {step['description']}")
        else:
            # Future step
            st.markdown(f"⏳ {step['name']}")
            if step.get('description'):
                st.caption(f"   {step['description']}")


def show_loading_skeleton(component_type: str = "table") -> None:
    """
    Show loading skeleton for different component types.
    
    Args:
        component_type: Type of component ("table", "cards", "metrics")
    """
    if component_type == "table":
        # Table skeleton
        st.markdown("""
        <div class="skeleton-table">
            <div class="skeleton-row skeleton-header"></div>
            <div class="skeleton-row"></div>
            <div class="skeleton-row"></div>
            <div class="skeleton-row"></div>
        </div>
        """, unsafe_allow_html=True)
    
    elif component_type == "cards":
        # Card skeleton
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="skeleton-card"></div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="skeleton-card"></div>', unsafe_allow_html=True)
    
    elif component_type == "metrics":
        # Metrics skeleton
        col1, col2, col3, col4 = st.columns(4)
        for col in [col1, col2, col3, col4]:
            with col:
                st.markdown('<div class="skeleton-metric"></div>', unsafe_allow_html=True)


def show_error_state(error_type: str, message: str, suggestions: Optional[List[str]] = None) -> None:
    """
    Show error state with helpful suggestions.
    
    Args:
        error_type: Type of error ("api", "validation", "network", "general")
        message: Error message to display
        suggestions: Optional list of suggestions to resolve the error
    """
    error_icons = {
        "api": "🔌",
        "validation": "⚠️",
        "network": "🌐",
        "general": "❌"
    }
    
    icon = error_icons.get(error_type, "❌")
    
    st.error(f"{icon} **Error:** {message}")
    
    if suggestions:
        st.markdown("**Suggestions to resolve this issue:**")
        for suggestion in suggestions:
            st.markdown(f"• {suggestion}")
    
    # Common troubleshooting
    with st.expander("🔧 General Troubleshooting", expanded=False):
        st.markdown("""
        **Common solutions:**
        - Check your internet connection
        - Verify your team key is correct
        - Try refreshing the page
        - Clear the application cache
        - Check if Yahoo Fantasy or MLB APIs are experiencing issues
        
        **If the problem persists:**
        - Try again in a few minutes
        - Contact support with the error details
        """)


def show_empty_state(component: str, action_text: str = "Get Started") -> None:
    """
    Show empty state with call to action.
    
    Args:
        component: Name of the component (e.g., "analysis", "roster")
        action_text: Text for the call to action
    """
    st.markdown(f"""
    <div style="text-align: center; padding: 3rem; color: #666;">
        <h3>📭 No {component.title()} Data</h3>
        <p>Click "{action_text}" to load your {component} information.</p>
    </div>
    """, unsafe_allow_html=True)


# CSS for loading animations and skeletons
LOADING_CSS = """
<style>
.loading-spinner {
    border: 4px solid #f3f3f3;
    border-top: 4px solid #ff6b6b;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
    margin: 0 auto 1rem auto;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.skeleton-table {
    width: 100%;
    margin: 1rem 0;
}

.skeleton-row {
    height: 20px;
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: loading 1.5s infinite;
    margin: 0.5rem 0;
    border-radius: 4px;
}

.skeleton-header {
    height: 30px;
    background: linear-gradient(90deg, #e0e0e0 25%, #d0d0d0 50%, #e0e0e0 75%);
}

.skeleton-card {
    height: 120px;
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: loading 1.5s infinite;
    border-radius: 8px;
    margin: 1rem 0;
}

.skeleton-metric {
    height: 80px;
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: loading 1.5s infinite;
    border-radius: 6px;
    margin: 0.5rem 0;
}

@keyframes loading {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}
</style>
"""


def inject_loading_css() -> None:
    """Inject loading CSS into the page."""
    st.markdown(LOADING_CSS, unsafe_allow_html=True)