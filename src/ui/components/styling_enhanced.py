"""
Enhanced styling with comprehensive dark mode and mobile-responsive design.

Provides automatic dark mode detection, mobile-first responsive design,
and improved accessibility for Yahoo Fantasy Baseball Streamlit application.
"""

import streamlit as st


def apply_enhanced_css() -> None:
    """Apply enhanced CSS with dark mode and mobile support."""
    st.markdown(get_enhanced_css(), unsafe_allow_html=True)
    
    # Add viewport meta tag for mobile
    st.markdown("""
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    """, unsafe_allow_html=True)


def get_enhanced_css() -> str:
    """Return comprehensive CSS with dark mode and mobile optimization."""
    return f"""
    <style>
    {get_enhanced_base_styles()}
    {get_dark_mode_styles()}
    {get_mobile_styles()}
    {get_enhanced_component_styles()}
    {get_enhanced_animations()}
    </style>
    """


def get_enhanced_base_styles() -> str:
    """Enhanced base styling with CSS variables for theming."""
    return """
    /* CSS Variables for Light Mode */
    :root {
        /* Primary Colors */
        --primary: #a73e3e;
        --primary-hover: #943636;
        --secondary: #4ecdc4;
        --secondary-hover: #26a69a;
        --accent: #2f7a9e;
        --accent-hover: #3a88ac;
        
        /* Status Colors */
        --success: #28a745;
        --warning: #ffc107;
        --error: #dc3545;
        --info: #17a2b8;
        
        /* Background Colors */
        --bg-primary: #ffffff;
        --bg-secondary: #f8f9fa;
        --bg-tertiary: #e9ecef;
        --bg-card: #ffffff;
        --bg-hover: #f1f3f5;
        
        /* Text Colors */
        --text-primary: #212529;
        --text-secondary: #6c757d;
        --text-muted: #adb5bd;
        --text-inverse: #ffffff;
        
        /* Border & Shadow */
        --border-color: #dee2e6;
        --border-radius: 12px;
        --border-radius-sm: 8px;
        --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.1);
        --shadow-md: 0 4px 8px rgba(0, 0, 0, 0.15);
        --shadow-lg: 0 8px 16px rgba(0, 0, 0, 0.2);
        
        /* Spacing */
        --spacing-xs: 0.25rem;
        --spacing-sm: 0.5rem;
        --spacing-md: 1rem;
        --spacing-lg: 1.5rem;
        --spacing-xl: 2rem;
        
        /* Transitions */
        --transition-fast: 0.15s ease;
        --transition-base: 0.3s ease;
        --transition-slow: 0.5s ease;
    }
    
    /* Global Resets */
    * {
        box-sizing: border-box;
    }
    
    /* Streamlit Container Adjustments */
    .stApp {
        background-color: var(--bg-primary);
        color: var(--text-primary);
        transition: background-color var(--transition-base);
    }
    
    .main .block-container {
        max-width: 1200px;
        padding: var(--spacing-lg);
        margin: 0 auto;
    }
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary);
        font-weight: 600;
        line-height: 1.3;
        margin-bottom: var(--spacing-md);
        transition: color var(--transition-base);
    }
    
    p {
        line-height: 1.6;
        color: var(--text-secondary);
    }
    
    a {
        color: var(--primary);
        text-decoration: none;
        transition: color var(--transition-fast);
    }
    
    a:hover {
        color: var(--primary-hover);
    }
    """


def get_dark_mode_styles() -> str:
    """Comprehensive dark mode styling with smooth transitions."""
    return """
    /* Dark Mode Variables */
    @media (prefers-color-scheme: dark) {
        :root {
            /* Primary Colors - Adjusted for dark mode */
            --primary: #c14949;
            --primary-hover: #d25555;
            --secondary: #5eddd4;
            --secondary-hover: #70e5dc;
            --accent: #4590b3;
            --accent-hover: #519ec1;
            
            /* Status Colors - Higher contrast for dark mode */
            --success: #52c41a;
            --warning: #faad14;
            --error: #ff4d4f;
            --info: #1890ff;
            
            /* Background Colors - Dark theme */
            --bg-primary: #0e1117;
            --bg-secondary: #1a1d23;
            --bg-tertiary: #262730;
            --bg-card: #1e2127;
            --bg-hover: #2a2d35;
            
            /* Text Colors - Dark theme */
            --text-primary: #e9ecef;
            --text-secondary: #adb5bd;
            --text-muted: #6c757d;
            --text-inverse: #0e1117;
            
            /* Border & Shadow - Dark theme */
            --border-color: #2d3139;
            --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.4);
            --shadow-md: 0 4px 8px rgba(0, 0, 0, 0.5);
            --shadow-lg: 0 8px 16px rgba(0, 0, 0, 0.6);
        }
        
        /* Dark Mode Specific Overrides */
        .stApp {
            background: linear-gradient(180deg, #0e1117 0%, #1a1d23 100%);
        }
        
        /* Sidebar Dark Mode */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1a1d23 0%, #262730 100%) !important;
            border-right: 1px solid var(--border-color);
        }
        
        section[data-testid="stSidebar"] .stMarkdown {
            color: var(--text-primary);
        }
        
        /* Input Fields Dark Mode */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > select,
        .stTextArea > div > div > textarea {
            background-color: var(--bg-tertiary) !important;
            color: var(--text-primary) !important;
            border-color: var(--border-color) !important;
        }
        
        /* Buttons Dark Mode */
        .stButton > button {
            background-color: var(--bg-card);
            color: var(--text-primary);
            border: 1px solid var(--border-color);
        }
        
        .stButton > button:hover {
            background-color: var(--bg-hover);
            border-color: var(--primary);
        }
        
        /* DataFrames Dark Mode */
        .stDataFrame {
            background-color: var(--bg-card);
        }
        
        .stDataFrame th {
            background: linear-gradient(135deg, var(--bg-tertiary), var(--bg-secondary));
            color: var(--text-primary);
        }
        
        .stDataFrame td {
            background-color: var(--bg-card);
            color: var(--text-secondary);
            border-color: var(--border-color);
        }
        
        .stDataFrame tr:hover td {
            background-color: var(--bg-hover);
        }
        
        /* Metrics Dark Mode */
        [data-testid="metric-container"] {
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--border-radius-sm);
            padding: var(--spacing-md);
        }
        
        /* Tabs Dark Mode */
        .stTabs [data-baseweb="tab-list"] {
            background-color: var(--bg-secondary);
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: var(--bg-card);
            color: var(--text-secondary);
            padding: 12px 20px;
            min-width: 120px;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, var(--primary), var(--primary-hover));
            color: var(--text-inverse);
        }
        
        /* Expander Dark Mode */
        .streamlit-expanderHeader {
            background-color: var(--bg-card);
            color: var(--text-primary);
            border: 1px solid var(--border-color);
        }
        
        .streamlit-expanderContent {
            background-color: var(--bg-secondary);
            border: 1px solid var(--border-color);
        }
        
        /* Loading Spinner Dark Mode */
        .stSpinner > div {
            border-color: var(--border-color);
            border-top-color: var(--primary);
        }
    }
    
    /* Dark Mode Toggle Animation */
    * {
        transition: background-color var(--transition-base), 
                    color var(--transition-base),
                    border-color var(--transition-base);
    }
    """


def get_mobile_styles() -> str:
    """Mobile-first responsive design with touch-friendly interfaces."""
    return """
    /* Mobile Styles - Touch Optimized */
    @media (max-width: 768px) {
        /* Container Adjustments */
        .main .block-container {
            padding: var(--spacing-sm);
            max-width: 100%;
        }
        
        /* Typography Scaling */
        h1 { font-size: 1.75rem; }
        h2 { font-size: 1.5rem; }
        h3 { font-size: 1.25rem; }
        p { font-size: 0.95rem; }
        
        /* Touch-Friendly Buttons */
        .stButton > button {
            min-height: 48px;
            padding: var(--spacing-md) var(--spacing-lg);
            font-size: 1rem;
            width: 100%;
        }
        
        /* Mobile Grid */
        .grid-2, .grid-3, .grid-4 {
            grid-template-columns: 1fr !important;
            gap: var(--spacing-md);
        }
        
        /* Card Adjustments */
        .player-card, .metric-card, .content-section {
            padding: var(--spacing-md);
            margin: var(--spacing-sm) 0;
            border-radius: var(--border-radius-sm);
        }
        
        /* Sidebar Mobile */
        section[data-testid="stSidebar"] {
            width: 100% !important;
            max-width: 100% !important;
        }
        
        /* Table Responsiveness */
        .stDataFrame {
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }
        
        .stDataFrame table {
            min-width: 100%;
            font-size: 0.875rem;
        }
        
        .stDataFrame th, .stDataFrame td {
            padding: var(--spacing-sm);
            white-space: nowrap;
        }
        
        /* Tab Mobile Optimization */
        .stTabs [data-baseweb="tab-list"] {
            flex-wrap: nowrap;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
            padding: var(--spacing-sm);
        }
        
        .stTabs [data-baseweb="tab"] {
            min-width: 120px;
            padding: var(--spacing-sm) var(--spacing-md);
            font-size: 0.9rem;
        }
        
        /* Input Fields Mobile */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > select {
            min-height: 44px;
            font-size: 16px; /* Prevents zoom on iOS */
            padding: var(--spacing-sm) var(--spacing-md);
        }
        
        /* Mobile Header */
        .main-header {
            padding: var(--spacing-md);
            border-radius: var(--border-radius-sm);
        }
        
        .main-header h1 {
            font-size: 1.5rem;
        }
        
        /* Mobile Header Row Layout */
        .stColumns [data-testid="column"] {
            padding: 0 var(--spacing-xs) !important;
        }
        
        .stButton > button {
            font-size: 0.85rem;
            padding: 6px 12px;
            white-space: nowrap;
        }
        
        /* Compact status text on mobile */
        .stCaption {
            font-size: 0.75rem;
        }
        
        /* Custom refresh button styling */
        button[data-testid="baseButton-secondary"][title="Refresh roster"] {
            background: rgba(0,0,0,0.7) !important;
            color: white !important;
            border: none !important;
            margin-top: -2.5rem !important;
            margin-left: 15rem !important;
            position: relative !important;
            z-index: 10 !important;
        }
        
        button[data-testid="baseButton-secondary"][title="Refresh roster"]:hover {
            background: rgba(0,0,0,0.8) !important;
        }
        
        /* Expander Mobile */
        .streamlit-expanderHeader {
            padding: var(--spacing-md);
            font-size: 1rem;
        }
        
        /* Metrics Mobile Layout */
        [data-testid="metric-container"] {
            width: 100%;
            margin-bottom: var(--spacing-md);
        }
        
        /* Mobile Navigation Helpers */
        .mobile-scroll-hint {
            display: block;
            text-align: center;
            color: var(--text-muted);
            font-size: 0.875rem;
            margin: var(--spacing-sm) 0;
        }
        
        /* Hide desktop-only elements */
        .desktop-only {
            display: none !important;
        }
        
        /* Show mobile-only elements */
        .mobile-only {
            display: block !important;
        }
    }
    
    /* Small Mobile Adjustments */
    @media (max-width: 480px) {
        h1 { font-size: 1.5rem; }
        h2 { font-size: 1.25rem; }
        h3 { font-size: 1.1rem; }
        
        .stButton > button {
            font-size: 0.9rem;
            padding: var(--spacing-sm) var(--spacing-md);
        }
        
        .player-card {
            padding: var(--spacing-sm);
        }
        
        .metric-value {
            font-size: 1.25rem;
        }
    }
    
    /* Landscape Mobile */
    @media (max-width: 768px) and (orientation: landscape) {
        .main-header {
            padding: var(--spacing-sm);
        }
        
        .main-header h1 {
            font-size: 1.25rem;
        }
    }
    
    /* Touch Device Optimizations */
    @media (hover: none) and (pointer: coarse) {
        /* Larger touch targets */
        button, a, input, select, textarea {
            min-height: 44px;
            min-width: 44px;
        }
        
        /* Remove hover effects on touch devices */
        .hover-lift:hover {
            transform: none;
        }
        
        /* Active states for touch */
        button:active, a:active {
            opacity: 0.8;
            transform: scale(0.98);
        }
    }
    
    /* Mobile-only helper classes */
    .mobile-only {
        display: none;
    }
    
    @media (max-width: 768px) {
        .mobile-only {
            display: block;
        }
    }
    """


def get_enhanced_component_styles() -> str:
    """Enhanced component styles with dark mode and mobile support."""
    return """
    /* Enhanced Card Components */
    .player-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        padding: var(--spacing-lg);
        margin: var(--spacing-md) 0;
        box-shadow: var(--shadow-sm);
        transition: all var(--transition-base);
        position: relative;
        overflow: hidden;
    }
    
    .player-card::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        height: 100%;
        width: 4px;
        background: var(--accent);
        transition: width var(--transition-base);
    }
    
    .player-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }
    
    .player-card:hover::before {
        width: 6px;
    }
    
    .player-card.my-team::before {
        background: var(--primary);
    }
    
    .player-card.high-owned::before {
        background: var(--success);
    }
    
    .player-card.low-owned::before {
        background: var(--warning);
    }
    
    /* Enhanced Metric Cards */
    .metric-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        padding: var(--spacing-lg);
        text-align: center;
        transition: all var(--transition-base);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--primary), var(--secondary));
        transform: scaleX(0);
        transition: transform var(--transition-base);
    }
    
    .metric-card:hover::after {
        transform: scaleX(1);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary);
        margin-bottom: var(--spacing-sm);
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Enhanced Status Badges */
    .status-badge {
        display: inline-block;
        padding: var(--spacing-xs) var(--spacing-md);
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        transition: all var(--transition-fast);
    }
    
    .status-badge.success {
        background: var(--success);
        color: white;
    }
    
    .status-badge.warning {
        background: var(--warning);
        color: var(--text-inverse);
    }
    
    .status-badge.info {
        background: var(--info);
        color: white;
    }
    
    .status-badge:hover {
        transform: scale(1.05);
        box-shadow: var(--shadow-sm);
    }
    
    /* Enhanced Section Headers */
    .section-header {
        background: linear-gradient(135deg, var(--bg-secondary), var(--bg-tertiary));
        padding: var(--spacing-lg);
        border-radius: var(--border-radius-sm);
        margin: var(--spacing-lg) 0;
        border-left: 4px solid var(--accent);
        position: relative;
    }
    
    .section-header h3 {
        margin: 0;
        color: var(--text-primary);
    }
    
    /* Content Sections */
    .content-section {
        background: var(--bg-card);
        padding: var(--spacing-xl);
        border-radius: var(--border-radius);
        margin: var(--spacing-md) 0;
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--border-color);
        transition: all var(--transition-base);
    }
    
    .content-section:hover {
        box-shadow: var(--shadow-md);
    }
    
    /* Main Header */
    .main-header {
        text-align: center;
        padding: var(--spacing-xl);
        background: linear-gradient(135deg, var(--primary), var(--accent));
        color: white;
        border-radius: var(--border-radius);
        margin-bottom: var(--spacing-xl);
        box-shadow: var(--shadow-md);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '⚾';
        position: absolute;
        right: -20px;
        top: -20px;
        font-size: 150px;
        opacity: 0.1;
        transform: rotate(-15deg);
    }
    
    .main-header h1 {
        color: white;
        margin: 0;
        position: relative;
        z-index: 1;
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.9);
        margin-top: var(--spacing-sm);
        position: relative;
        z-index: 1;
    }
    """


def get_enhanced_animations() -> str:
    """Enhanced animations for smooth transitions."""
    return """
    /* Keyframe Animations */
    @keyframes fadeIn {
        from { 
            opacity: 0; 
            transform: translateY(20px); 
        }
        to { 
            opacity: 1; 
            transform: translateY(0); 
        }
    }
    
    @keyframes slideIn {
        from { 
            transform: translateX(-100%); 
            opacity: 0;
        }
        to { 
            transform: translateX(0); 
            opacity: 1;
        }
    }
    
    @keyframes pulse {
        0%, 100% { 
            transform: scale(1); 
        }
        50% { 
            transform: scale(1.05); 
        }
    }
    
    @keyframes shimmer {
        0% { 
            background-position: -200% center; 
        }
        100% { 
            background-position: 200% center; 
        }
    }
    
    @keyframes spin {
        from { 
            transform: rotate(0deg); 
        }
        to { 
            transform: rotate(360deg); 
        }
    }
    
    /* Animation Classes */
    .fade-in {
        animation: fadeIn 0.6s ease-out forwards;
    }
    
    .slide-in {
        animation: slideIn 0.5s ease-out forwards;
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    /* Loading States */
    .loading-shimmer {
        background: linear-gradient(
            90deg,
            var(--bg-secondary) 25%,
            var(--bg-tertiary) 50%,
            var(--bg-secondary) 75%
        );
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
    }
    
    /* Skeleton Loader */
    .skeleton {
        background: var(--bg-tertiary);
        border-radius: var(--border-radius-sm);
        position: relative;
        overflow: hidden;
    }
    
    .skeleton::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(
            90deg,
            transparent,
            rgba(255, 255, 255, 0.1),
            transparent
        );
        animation: shimmer 1.5s infinite;
    }
    
    /* Smooth Transitions */
    .transition-all {
        transition: all var(--transition-base);
    }
    
    .transition-colors {
        transition: background-color var(--transition-base), 
                    color var(--transition-base),
                    border-color var(--transition-base);
    }
    
    .transition-transform {
        transition: transform var(--transition-base);
    }
    
    /* Hover Effects */
    .hover-lift {
        transition: transform var(--transition-base), 
                    box-shadow var(--transition-base);
    }
    
    .hover-lift:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-lg);
    }
    
    .hover-scale {
        transition: transform var(--transition-fast);
    }
    
    .hover-scale:hover {
        transform: scale(1.05);
    }
    
    /* Focus States */
    input:focus,
    select:focus,
    textarea:focus,
    button:focus {
        outline: none;
        box-shadow: 0 0 0 3px rgba(255, 107, 107, 0.2);
        border-color: var(--primary);
    }
    
    /* Reduce Motion for Accessibility */
    @media (prefers-reduced-motion: reduce) {
        *,
        *::before,
        *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }
    """