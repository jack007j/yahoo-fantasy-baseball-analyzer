"""
Professional styling and CSS components for Yahoo Fantasy Baseball Streamlit application.

Provides consistent visual design and enhanced user experience.
"""

import streamlit as st


def apply_custom_css() -> None:
    """Apply custom CSS styling to the application."""
    st.markdown(get_custom_css(), unsafe_allow_html=True)


def get_custom_css() -> str:
    """Return the complete custom CSS for the application."""
    return f"""
    <style>
    {get_base_styles()}
    {get_component_styles()}
    {get_layout_styles()}
    {get_animation_styles()}
    {get_responsive_styles()}
    </style>
    """


def get_base_styles() -> str:
    """Base styling for typography, colors, and general elements."""
    return """
    /* Base Typography and Colors */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Custom color scheme */
    :root {
        --primary-color: #ff6b6b;
        --secondary-color: #4ecdc4;
        --accent-color: #45b7d1;
        --success-color: #28a745;
        --warning-color: #ffc107;
        --error-color: #dc3545;
        --info-color: #17a2b8;
        --dark-color: #343a40;
        --light-color: #f8f9fa;
        --border-color: #dee2e6;
        --shadow-color: rgba(0, 0, 0, 0.1);
    }
    
    /* Enhanced headers */
    h1, h2, h3 {
        color: var(--dark-color);
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    h1 {
        border-bottom: 3px solid var(--primary-color);
        padding-bottom: 0.5rem;
    }
    
    h2 {
        border-left: 4px solid var(--secondary-color);
        padding-left: 1rem;
    }
    
    /* Enhanced text styling */
    .stMarkdown p {
        line-height: 1.6;
        color: #333;
    }
    
    /* Custom caption styling */
    .caption {
        font-size: 0.85rem;
        color: #666;
        font-style: italic;
    }
    """


def get_component_styles() -> str:
    """Styling for specific UI components."""
    return """
    /* Button Enhancements */
    .stButton > button {
        border-radius: 8px;
        border: none;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px var(--shadow-color);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px var(--shadow-color);
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--primary-color), #ff5252);
    }
    
    .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, var(--secondary-color), #26a69a);
    }
    
    /* Metric Cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px var(--shadow-color);
        border: 1px solid var(--border-color);
        transition: transform 0.3s ease;
        margin: 0.5rem 0;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 16px var(--shadow-color);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary-color);
        margin: 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Player Cards */
    .player-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px var(--shadow-color);
        border-left: 4px solid var(--accent-color);
        transition: all 0.3s ease;
    }
    
    .player-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px var(--shadow-color);
    }
    
    .player-card.high-owned {
        border-left-color: var(--success-color);
    }
    
    .player-card.low-owned {
        border-left-color: var(--warning-color);
    }
    
    .player-card.my-team {
        border-left-color: var(--primary-color);
        background: linear-gradient(135deg, #fff, #fff8f8);
    }
    
    .player-name {
        font-size: 1.2rem;
        font-weight: 600;
        color: var(--dark-color);
        margin: 0 0 0.5rem 0;
    }
    
    .player-details {
        font-size: 0.9rem;
        color: #666;
        margin: 0.25rem 0;
    }
    
    /* Status Badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .status-badge.success {
        background: var(--success-color);
        color: white;
    }
    
    .status-badge.warning {
        background: var(--warning-color);
        color: var(--dark-color);
    }
    
    .status-badge.info {
        background: var(--info-color);
        color: white;
    }
    
    .status-badge.secondary {
        background: var(--secondary-color);
        color: white;
    }
    
    /* Enhanced Tables */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px var(--shadow-color);
    }
    
    .stDataFrame table {
        border-collapse: collapse;
    }
    
    .stDataFrame th {
        background: linear-gradient(135deg, var(--primary-color), #ff5252);
        color: white;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding: 1rem 0.75rem;
    }
    
    .stDataFrame td {
        padding: 0.75rem;
        border-bottom: 1px solid var(--border-color);
    }
    
    .stDataFrame tr:hover {
        background-color: #f8f9fa;
    }
    """


def get_layout_styles() -> str:
    """Layout and spacing styles."""
    return """
    /* Layout Enhancements */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 8px var(--shadow-color);
    }
    
    .section-header {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        padding: 1.5rem;
        border-radius: 8px;
        margin: 2rem 0 1rem 0;
        border-left: 4px solid var(--accent-color);
    }
    
    .content-section {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 2px 4px var(--shadow-color);
        border: 1px solid var(--border-color);
    }
    
    /* Grid Layouts */
    .grid-2 {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .grid-3 {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .grid-4 {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin: 1rem 0;
    }
    
    /* Sidebar Enhancements */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa, #e9ecef);
    }
    
    .sidebar-section {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        box-shadow: 0 2px 4px var(--shadow-color);
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: var(--light-color);
        padding: 0.5rem;
        border-radius: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        padding: 0 1.5rem;
        background: white;
        border-radius: 6px;
        border: 1px solid var(--border-color);
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: var(--light-color);
        transform: translateY(-1px);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary-color), #ff5252);
        color: white;
        border-color: var(--primary-color);
    }
    """


def get_animation_styles() -> str:
    """Animation and transition styles."""
    return """
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideIn {
        from { transform: translateX(-100%); }
        to { transform: translateX(0); }
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    @keyframes shimmer {
        0% { background-position: -200px 0; }
        100% { background-position: calc(200px + 100%) 0; }
    }
    
    .fade-in {
        animation: fadeIn 0.6s ease-out;
    }
    
    .slide-in {
        animation: slideIn 0.5s ease-out;
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    /* Loading States */
    .loading-shimmer {
        background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
        background-size: 200px 100%;
        animation: shimmer 1.5s infinite;
    }
    
    /* Hover Effects */
    .hover-lift {
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .hover-lift:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 16px var(--shadow-color);
    }
    
    /* Focus States */
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > div:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 2px rgba(255, 107, 107, 0.2);
    }
    """


def get_responsive_styles() -> str:
    """Responsive design styles for different screen sizes."""
    return """
    /* Responsive Design */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        .grid-2, .grid-3, .grid-4 {
            grid-template-columns: 1fr;
        }
        
        .player-card {
            padding: 1rem;
        }
        
        .metric-card {
            padding: 1rem;
        }
        
        .main-header {
            padding: 1rem;
        }
        
        .content-section {
            padding: 1rem;
        }
    }
    
    @media (max-width: 480px) {
        .stTabs [data-baseweb="tab"] {
            padding: 0 0.75rem;
            font-size: 0.9rem;
        }
        
        .player-name {
            font-size: 1rem;
        }
        
        .metric-value {
            font-size: 1.5rem;
        }
    }
    
    /* Print Styles */
    @media print {
        .stButton, .stSelectbox, .stTextInput {
            display: none;
        }
        
        .player-card, .metric-card {
            box-shadow: none;
            border: 1px solid var(--border-color);
        }
        
        .main-header {
            background: white;
            color: var(--dark-color);
            border: 2px solid var(--primary-color);
        }
    }
    """


def create_metric_card(title: str, value: str, delta: str = "", help_text: str = "") -> str:
    """
    Create a custom metric card with enhanced styling.
    
    Args:
        title: Metric title
        value: Metric value
        delta: Optional delta/change value
        help_text: Optional help text
        
    Returns:
        HTML string for the metric card
    """
    delta_html = f'<div class="metric-delta">{delta}</div>' if delta else ''
    help_html = f'<div class="metric-help">{help_text}</div>' if help_text else ''
    
    return f"""
    <div class="metric-card hover-lift">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{title}</div>
        {delta_html}
        {help_html}
    </div>
    """


def create_player_card(
    name: str, 
    positions: str, 
    team: str, 
    ownership: str, 
    source: str = "",
    additional_info: str = "",
    card_type: str = "default"
) -> str:
    """
    Create a custom player card with enhanced styling.
    
    Args:
        name: Player name
        positions: Player positions
        team: MLB team
        ownership: Ownership percentage
        source: Player source (My Team, Waiver, etc.)
        additional_info: Additional information
        card_type: Card type for styling (default, high-owned, low-owned, my-team)
        
    Returns:
        HTML string for the player card
    """
    card_class = f"player-card {card_type} hover-lift fade-in"
    source_html = f'<div class="player-details"><strong>Source:</strong> {source}</div>' if source else ''
    info_html = f'<div class="player-details">{additional_info}</div>' if additional_info else ''
    
    return f"""
    <div class="{card_class}">
        <div class="player-name">{name}</div>
        <div class="player-details"><strong>Positions:</strong> {positions}</div>
        <div class="player-details"><strong>Team:</strong> {team}</div>
        <div class="player-details"><strong>Ownership:</strong> {ownership}</div>
        {source_html}
        {info_html}
    </div>
    """


def create_status_badge(text: str, status_type: str = "info") -> str:
    """
    Create a status badge with appropriate styling.
    
    Args:
        text: Badge text
        status_type: Badge type (success, warning, info, secondary)
        
    Returns:
        HTML string for the status badge
    """
    return f'<span class="status-badge {status_type}">{text}</span>'


def create_section_header(title: str, subtitle: str = "") -> str:
    """
    Create a styled section header.
    
    Args:
        title: Section title
        subtitle: Optional subtitle
        
    Returns:
        HTML string for the section header
    """
    subtitle_html = f'<div style="font-size: 0.9rem; color: #666; margin-top: 0.5rem;">{subtitle}</div>' if subtitle else ''
    
    return f"""
    <div class="section-header fade-in">
        <h3 style="margin: 0; color: var(--dark-color);">{title}</h3>
        {subtitle_html}
    </div>
    """


def show_loading_overlay(message: str = "Loading...") -> None:
    """Show a loading overlay with custom styling."""
    st.markdown(f"""
    <div style="
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(255, 255, 255, 0.9);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
        flex-direction: column;
    ">
        <div class="loading-spinner" style="
            border: 4px solid #f3f3f3;
            border-top: 4px solid var(--primary-color);
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin-bottom: 1rem;
        "></div>
        <div style="font-size: 1.2rem; color: var(--dark-color);">{message}</div>
    </div>
    """, unsafe_allow_html=True)