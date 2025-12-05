"""Dark Mode and Glassmorphism CSS styles for ClaimsIQ Nexus.

Provides consistent styling across the application with a modern,
professional appearance suitable for healthcare/enterprise applications.
"""

# Color palette
COLORS = {
    "primary": "#6366f1",  # Indigo
    "primary_dark": "#4f46e5",
    "secondary": "#8b5cf6",  # Purple
    "success": "#10b981",  # Emerald
    "warning": "#f59e0b",  # Amber
    "danger": "#ef4444",  # Red
    "info": "#3b82f6",  # Blue
    "background": "#0f172a",  # Slate 900
    "surface": "#1e293b",  # Slate 800
    "surface_light": "#334155",  # Slate 700
    "text_primary": "#f8fafc",  # Slate 50
    "text_secondary": "#94a3b8",  # Slate 400
    "text_muted": "#64748b",  # Slate 500
    "border": "#475569",  # Slate 600
    "glass_bg": "rgba(30, 41, 59, 0.8)",
    "glass_border": "rgba(255, 255, 255, 0.1)",
}


def get_dark_mode_css() -> str:
    """Get the main dark mode CSS for the application."""
    return f"""
    <style>
    /* Global Dark Mode */
    .stApp {{
        background-color: {COLORS['background']};
        color: {COLORS['text_primary']};
    }}

    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}

    /* Main container */
    .main .block-container {{
        padding: 2rem 1rem;
        max-width: 100%;
    }}

    /* Headers */
    h1, h2, h3, h4, h5, h6 {{
        color: {COLORS['text_primary']} !important;
    }}

    /* Text */
    p, span, label {{
        color: {COLORS['text_secondary']};
    }}

    /* Links */
    a {{
        color: {COLORS['primary']} !important;
    }}
    a:hover {{
        color: {COLORS['secondary']} !important;
    }}

    /* Glassmorphism card */
    .glass-card {{
        background: {COLORS['glass_bg']};
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid {COLORS['glass_border']};
        border-radius: 16px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }}

    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {{
        background-color: {COLORS['surface']} !important;
        color: {COLORS['text_primary']} !important;
        border: 1px solid {COLORS['border']} !important;
        border-radius: 8px !important;
    }}

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: {COLORS['primary']} !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
    }}

    /* Buttons */
    .stButton > button {{
        background-color: {COLORS['primary']} !important;
        color: {COLORS['text_primary']} !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }}

    .stButton > button:hover {{
        background-color: {COLORS['primary_dark']} !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4) !important;
    }}

    /* Chat message containers */
    .stChatMessage {{
        background-color: {COLORS['surface']} !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        margin: 0.5rem 0 !important;
    }}

    /* Chat input */
    .stChatInput {{
        background-color: {COLORS['surface']} !important;
        border: 1px solid {COLORS['border']} !important;
        border-radius: 12px !important;
    }}

    .stChatInput > div {{
        background-color: {COLORS['surface']} !important;
    }}

    /* Expander */
    .streamlit-expanderHeader {{
        background-color: {COLORS['surface']} !important;
        border-radius: 8px !important;
        color: {COLORS['text_primary']} !important;
    }}

    .streamlit-expanderContent {{
        background-color: {COLORS['surface_light']} !important;
        border-radius: 0 0 8px 8px !important;
    }}

    /* Spinner */
    .stSpinner > div {{
        border-color: {COLORS['primary']} transparent transparent transparent !important;
    }}

    /* Status containers */
    .stAlert {{
        background-color: {COLORS['surface']} !important;
        border-radius: 8px !important;
    }}

    /* Metrics */
    .stMetric {{
        background-color: {COLORS['surface']} !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }}

    .stMetric label {{
        color: {COLORS['text_muted']} !important;
    }}

    .stMetric [data-testid="stMetricValue"] {{
        color: {COLORS['text_primary']} !important;
        font-size: 2rem !important;
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: {COLORS['surface']} !important;
        border-radius: 8px !important;
        padding: 0.25rem !important;
    }}

    .stTabs [data-baseweb="tab"] {{
        color: {COLORS['text_secondary']} !important;
    }}

    .stTabs [data-baseweb="tab"][aria-selected="true"] {{
        background-color: {COLORS['primary']} !important;
        color: {COLORS['text_primary']} !important;
        border-radius: 6px !important;
    }}

    /* Divider */
    hr {{
        border-color: {COLORS['border']} !important;
    }}

    /* Scrollbar */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}

    ::-webkit-scrollbar-track {{
        background: {COLORS['surface']};
    }}

    ::-webkit-scrollbar-thumb {{
        background: {COLORS['surface_light']};
        border-radius: 4px;
    }}

    ::-webkit-scrollbar-thumb:hover {{
        background: {COLORS['border']};
    }}

    /* Plotly charts background */
    .js-plotly-plot .plotly {{
        background-color: transparent !important;
    }}

    /* Custom status badges */
    .status-badge {{
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }}

    .status-approved {{
        background-color: rgba(16, 185, 129, 0.2);
        color: {COLORS['success']};
    }}

    .status-denied {{
        background-color: rgba(239, 68, 68, 0.2);
        color: {COLORS['danger']};
    }}

    .status-pending {{
        background-color: rgba(245, 158, 11, 0.2);
        color: {COLORS['warning']};
    }}

    /* Risk score indicators */
    .risk-high {{
        color: {COLORS['danger']};
    }}

    .risk-medium {{
        color: {COLORS['warning']};
    }}

    .risk-low {{
        color: {COLORS['success']};
    }}
    </style>
    """


def get_canvas_css() -> str:
    """Get CSS specifically for the Canvas panel."""
    return f"""
    <style>
    /* Canvas container */
    .canvas-container {{
        background: {COLORS['glass_bg']};
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid {COLORS['glass_border']};
        border-radius: 16px;
        padding: 1.5rem;
        min-height: 70vh;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }}

    /* Canvas header */
    .canvas-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid {COLORS['border']};
    }}

    .canvas-title {{
        font-size: 1.25rem;
        font-weight: 600;
        color: {COLORS['text_primary']};
        margin: 0;
    }}

    .canvas-subtitle {{
        font-size: 0.875rem;
        color: {COLORS['text_muted']};
    }}

    /* Empty state splash */
    .empty-splash {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 60vh;
        text-align: center;
    }}

    .empty-splash-icon {{
        font-size: 4rem;
        margin-bottom: 1rem;
        opacity: 0.5;
    }}

    .empty-splash-title {{
        font-size: 1.5rem;
        font-weight: 600;
        color: {COLORS['text_primary']};
        margin-bottom: 0.5rem;
    }}

    .empty-splash-subtitle {{
        color: {COLORS['text_muted']};
        max-width: 400px;
    }}

    /* Clinical note viewer */
    .clinical-note {{
        background: {COLORS['surface']};
        border-radius: 12px;
        padding: 1.5rem;
        font-family: 'Georgia', serif;
        line-height: 1.7;
    }}

    .clinical-note h1, .clinical-note h2 {{
        color: {COLORS['primary']};
        border-bottom: 1px solid {COLORS['border']};
        padding-bottom: 0.5rem;
    }}

    .clinical-note strong {{
        color: {COLORS['warning']};
    }}

    /* Claim card */
    .claim-card {{
        background: {COLORS['surface']};
        border-radius: 12px;
        padding: 1.5rem;
    }}

    .claim-card-header {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 1.5rem;
    }}

    .claim-field {{
        margin-bottom: 1rem;
    }}

    .claim-field-label {{
        font-size: 0.75rem;
        color: {COLORS['text_muted']};
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}

    .claim-field-value {{
        font-size: 1rem;
        color: {COLORS['text_primary']};
        font-weight: 500;
    }}
    </style>
    """


def render_status_badge(status: str) -> str:
    """Render an HTML status badge.

    Args:
        status: One of 'Approved', 'Denied', 'Pending'

    Returns:
        HTML string for the badge
    """
    status_lower = status.lower()
    css_class = f"status-{status_lower}"
    return f'<span class="status-badge {css_class}">{status}</span>'


def render_risk_indicator(score: float) -> str:
    """Render a risk score with color coding.

    Args:
        score: Risk score between 0 and 1

    Returns:
        HTML string with colored risk indicator
    """
    if score >= 0.7:
        css_class = "risk-high"
        label = "High Risk"
    elif score >= 0.4:
        css_class = "risk-medium"
        label = "Medium Risk"
    else:
        css_class = "risk-low"
        label = "Low Risk"

    percentage = int(score * 100)
    return f'<span class="{css_class}">{label} ({percentage}%)</span>'
