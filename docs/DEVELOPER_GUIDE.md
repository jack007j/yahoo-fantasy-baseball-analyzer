# Developer Guide - Yahoo Fantasy Baseball Analyzer

A comprehensive guide for developers working on the Yahoo Fantasy Baseball Analyzer application.

## 📚 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Development Setup](#development-setup)
3. [Code Structure](#code-structure)
4. [API Integration](#api-integration)
5. [Data Models](#data-models)
6. [UI Components](#ui-components)
7. [Testing Strategy](#testing-strategy)
8. [Deployment](#deployment)
9. [Contributing Guidelines](#contributing-guidelines)

## 🏗️ Architecture Overview

### System Architecture

The application follows a layered architecture pattern:

```
┌─────────────────────────────────────────┐
│                UI Layer                 │
│  (Streamlit Components & Pages)         │
├─────────────────────────────────────────┤
│              Service Layer              │
│  (Business Logic & Analysis)            │
├─────────────────────────────────────────┤
│               API Layer                 │
│  (Yahoo Fantasy & MLB Stats APIs)       │
├─────────────────────────────────────────┤
│              Data Layer                 │
│  (Models & Caching)                     │
└─────────────────────────────────────────┘
```

### Design Patterns

- **Repository Pattern**: API clients abstract data access
- **Service Layer Pattern**: Business logic separated from UI
- **Model-View Pattern**: Pydantic models for data validation
- **Dependency Injection**: Services injected into UI components
- **Caching Strategy**: Multi-level caching for performance

### Technology Stack

- **Frontend**: Streamlit (Python web framework)
- **Backend**: Python 3.8+
- **APIs**: Yahoo Fantasy API, MLB Stats API
- **Data Validation**: Pydantic
- **HTTP Client**: Requests
- **Caching**: Streamlit built-in + custom service
- **Testing**: Pytest
- **Deployment**: Streamlit Cloud

## 🛠️ Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Yahoo Developer Account
- Code editor (VS Code recommended)

### Local Development Environment

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd yahoo-fantasy-baseball-streamlit
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

2. **Environment Configuration**
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   # Edit secrets.toml with your credentials
   ```

3. **Run Development Server**
   ```bash
   streamlit run app.py
   ```

### Development Dependencies

```txt
# requirements-dev.txt
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0
black>=22.0.0
flake8>=5.0.0
mypy>=1.0.0
pre-commit>=2.20.0
```

### Code Quality Tools

#### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.10.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 5.0.4
    hooks:
      - id: flake8
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.0
    hooks:
      - id: mypy
```

#### Setup Pre-commit
```bash
pre-commit install
```

## 📁 Code Structure

### Directory Layout

```
src/
├── api/                    # External API integrations
│   ├── __init__.py
│   ├── base_client.py      # Base API client with common functionality
│   ├── yahoo_client.py     # Yahoo Fantasy API client
│   └── mlb_client.py       # MLB Stats API client
├── core/                   # Core application functionality
│   ├── __init__.py
│   ├── config.py           # Configuration management
│   ├── constants.py        # Application constants
│   ├── exceptions.py       # Custom exception classes
│   └── logging_config.py   # Logging configuration
├── models/                 # Data models and schemas
│   ├── __init__.py
│   ├── player.py           # Player data model
│   ├── team.py             # Team data model
│   └── analysis.py         # Analysis result models
├── services/               # Business logic services
│   ├── __init__.py
│   ├── analysis_service.py # Main analysis logic
│   └── cache_service.py    # Caching service
├── ui/                     # User interface components
│   ├── __init__.py
│   ├── components/         # Reusable UI components
│   │   ├── __init__.py
│   │   ├── sidebar.py      # Sidebar configuration
│   │   ├── styling.py      # CSS and styling
│   │   └── loading.py      # Loading indicators
│   └── pages/              # Page-level components
│       ├── __init__.py
│       ├── analysis_tab.py # Analysis results page
│       └── roster_tab.py   # Roster management page
└── utils/                  # Utility functions
    ├── __init__.py
    ├── date_utils.py       # Date manipulation utilities
    ├── text_utils.py       # Text processing utilities
    └── url_utils.py        # URL handling utilities
```

### Key Files

#### `app.py` - Main Application Entry Point
```python
"""
Main Streamlit application entry point.
Handles page configuration, routing, and error handling.
"""

def main() -> None:
    """Main application entry point."""
    # Page configuration
    st.set_page_config(...)
    
    # Initialize configuration
    config = get_config()
    
    # Render UI components
    render_sidebar()
    render_main_content()
```

#### `src/core/config.py` - Configuration Management
```python
"""
Centralized configuration management using Pydantic models.
Handles secrets loading, validation, and environment-specific settings.
"""

class ApplicationConfiguration:
    """Main configuration manager."""
    
    def __init__(self) -> None:
        self._load_configuration()
    
    def _load_configuration(self) -> None:
        """Load and validate configuration from Streamlit secrets."""
```

## 🔌 API Integration

### Base API Client

All API clients inherit from `BaseAPIClient`:

```python
# src/api/base_client.py
class BaseAPIClient:
    """Base class for all API clients."""
    
    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Make HTTP request with error handling and retries."""
        # Implementation with retry logic, error handling
```

### Yahoo Fantasy API Client

```python
# src/api/yahoo_client.py
class YahooFantasyClient(BaseAPIClient):
    """Client for Yahoo Fantasy Sports API."""
    
    def __init__(self, oauth_config: YahooOAuthConfig):
        super().__init__("https://fantasysports.yahooapis.com/fantasy/v2")
        self.oauth_config = oauth_config
        self._setup_oauth()
    
    def get_team_roster(self, team_key: str) -> List[Player]:
        """Fetch team roster from Yahoo API."""
        # Implementation
    
    def get_league_settings(self, league_id: str) -> LeagueSettings:
        """Fetch league configuration."""
        # Implementation
```

### MLB Stats API Client

```python
# src/api/mlb_client.py
class MLBStatsClient(BaseAPIClient):
    """Client for MLB Stats API."""
    
    def __init__(self):
        super().__init__("https://statsapi.mlb.com/api/v1")
    
    def get_probable_pitchers(self, date: date) -> List[ProbablePitcher]:
        """Fetch probable pitchers for given date."""
        # Implementation
    
    def get_schedule(self, start_date: date, end_date: date) -> List[Game]:
        """Fetch MLB schedule for date range."""
        # Implementation
```

### Error Handling

```python
# src/core/exceptions.py
class APIError(Exception):
    """Base exception for API-related errors."""
    pass

class YahooAPIError(APIError):
    """Yahoo Fantasy API specific errors."""
    pass

class MLBAPIError(APIError):
    """MLB Stats API specific errors."""
    pass

class RateLimitError(APIError):
    """Rate limiting errors."""
    pass
```

## 📊 Data Models

### Pydantic Models

All data models use Pydantic for validation:

```python
# src/models/player.py
class Player(BaseModel):
    """Player data model."""
    
    player_id: str
    name: str
    positions: List[str]
    mlb_team: Optional[str] = None
    percent_owned: float = 0.0
    source: Literal["My Team", "Waiver"] = "Waiver"
    
    @validator('positions')
    def validate_positions(cls, v):
        """Validate position list."""
        if not v:
            raise ValueError("Player must have at least one position")
        return v
    
    @property
    def display_positions(self) -> str:
        """Format positions for display."""
        return ", ".join(self.positions)
```

```python
# src/models/analysis.py
class PitcherAnalysis(BaseModel):
    """Analysis result for a single pitcher."""
    
    player: Player
    confirmed_start_date: Optional[date] = None
    potential_second_start: bool = False
    recommendation_reason: Optional[str] = None
    confidence_score: float = 0.0
    
    @property
    def start_date_display(self) -> str:
        """Format start date for display."""
        if self.confirmed_start_date:
            return self.confirmed_start_date.strftime("%A, %B %d")
        return "TBD"
```

### Data Flow

```
Yahoo API → Player Models → Analysis Service → PitcherAnalysis → UI Display
    ↓
MLB API → Game/Pitcher Data → Analysis Logic → Recommendations → User Actions
```

## 🎨 UI Components

### Streamlit Component Architecture

#### Page Structure
```python
# src/ui/pages/analysis_tab.py
def render_analysis_tab() -> None:
    """Render the main analysis tab."""
    
    # Check configuration
    if not _is_configured():
        _show_configuration_prompt()
        return
    
    # Analysis controls
    _render_analysis_controls()
    
    # Results display
    if 'analysis_results' in st.session_state:
        _display_results(st.session_state['analysis_results'])
    else:
        _show_placeholder()
```

#### Reusable Components
```python
# src/ui/components/sidebar.py
def render_sidebar() -> Dict[str, Any]:
    """Render sidebar with configuration options."""
    
    # Team configuration
    team_key = _render_team_input()
    
    # Analysis settings
    settings = _render_analysis_settings()
    
    # Help sections
    _render_help_sections()
    
    return {
        'team_key': team_key,
        'settings': settings,
        'is_configured': bool(team_key)
    }
```

### Styling and CSS

```python
# src/ui/components/styling.py
def apply_custom_css() -> None:
    """Apply custom CSS styling."""
    
    css = """
    <style>
    .main-header {
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .content-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
        margin: 1rem 0;
    }
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)
```

## 🧪 Testing Strategy

### Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Pytest configuration and fixtures
├── unit/                    # Unit tests
│   ├── test_models.py       # Model validation tests
│   ├── test_services.py     # Service logic tests
│   └── test_utils.py        # Utility function tests
├── integration/             # Integration tests
│   ├── test_api_clients.py  # API client tests
│   └── test_analysis.py     # End-to-end analysis tests
└── fixtures/                # Test data fixtures
    ├── yahoo_responses.json
    └── mlb_responses.json
```

### Test Examples

#### Unit Tests
```python
# tests/unit/test_models.py
import pytest
from src.models.player import Player

def test_player_validation():
    """Test player model validation."""
    
    # Valid player
    player = Player(
        player_id="123",
        name="Test Player",
        positions=["SP"],
        percent_owned=25.5
    )
    assert player.display_positions == "SP"
    
    # Invalid player (no positions)
    with pytest.raises(ValueError):
        Player(
            player_id="123",
            name="Test Player",
            positions=[]
        )
```

#### Integration Tests
```python
# tests/integration/test_analysis.py
import pytest
from unittest.mock import Mock, patch
from src.services.analysis_service import AnalysisService

@patch('src.api.yahoo_client.YahooFantasyClient')
@patch('src.api.mlb_client.MLBStatsClient')
def test_analysis_service_integration(mock_mlb, mock_yahoo):
    """Test complete analysis workflow."""
    
    # Setup mocks
    mock_yahoo.return_value.get_team_roster.return_value = [...]
    mock_mlb.return_value.get_probable_pitchers.return_value = [...]
    
    # Run analysis
    service = AnalysisService(mock_yahoo, mock_mlb, Mock())
    results = service.analyze_next_fantasy_week("458.l.135626.t.6")
    
    # Verify results
    assert len(results) > 0
    assert all(isinstance(r, PitcherAnalysis) for r in results)
```

### Test Fixtures

```python
# tests/conftest.py
import pytest
from src.models.player import Player

@pytest.fixture
def sample_player():
    """Sample player for testing."""
    return Player(
        player_id="123",
        name="Test Pitcher",
        positions=["SP"],
        mlb_team="NYY",
        percent_owned=15.0,
        source="Waiver"
    )

@pytest.fixture
def mock_yahoo_response():
    """Mock Yahoo API response."""
    return {
        "fantasy_content": {
            "team": {
                "roster": {
                    "players": [...]
                }
            }
        }
    }
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_models.py

# Run with verbose output
pytest -v

# Run integration tests only
pytest tests/integration/
```

## 🚀 Deployment

### Streamlit Cloud Deployment

#### Preparation
1. **Repository Setup**
   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

2. **Requirements Check**
   - Ensure `requirements.txt` is complete
   - Verify `app.py` is in root directory
   - Check `.streamlit/config.toml` settings

#### Deployment Process
1. **Connect Repository**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect GitHub account
   - Select repository

2. **Configure Deployment**
   - Branch: `main`
   - Main file path: `app.py`
   - Python version: 3.8+

3. **Set Secrets**
   ```toml
   # In Streamlit Cloud secrets section
   [yahoo_oauth]
   client_id = "production_client_id"
   client_secret = "production_client_secret"
   access_token = "production_access_token"
   refresh_token = "production_refresh_token"
   
   [app_config]
   default_league_id = "458.l.135626"
   default_team_key = "458.l.135626.t.6"
   cache_ttl_seconds = 3600
   max_retries = 3
   request_timeout = 10
   ```

### Environment-Specific Configuration

```python
# src/core/config.py
def get_environment() -> str:
    """Determine current environment."""
    if "streamlit.io" in os.environ.get("HOSTNAME", ""):
        return "production"
    return "development"

class ApplicationConfiguration:
    def __init__(self):
        self.environment = get_environment()
        self._load_configuration()
    
    def _load_configuration(self):
        """Load environment-specific configuration."""
        if self.environment == "production":
            # Production-specific settings
            self.cache_ttl = 3600  # 1 hour
            self.log_level = "INFO"
        else:
            # Development settings
            self.cache_ttl = 300   # 5 minutes
            self.log_level = "DEBUG"
```

### Monitoring and Logging

```python
# src/core/logging_config.py
import logging
import streamlit as st

def setup_logging(level: str = "INFO"):
    """Configure application logging."""
    
    logging.basicConfig(
        level=getattr(logging, level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            # Add file handler for production
        ]
    )
    
    # Suppress noisy loggers
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

def log_user_action(action: str, details: dict = None):
    """Log user actions for analytics."""
    logger = logging.getLogger("user_actions")
    logger.info(f"Action: {action}, Details: {details}")
```

## 🤝 Contributing Guidelines

### Development Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/new-feature-name
   ```

2. **Make Changes**
   - Follow code style guidelines
   - Add tests for new functionality
   - Update documentation

3. **Run Quality Checks**
   ```bash
   # Code formatting
   black src/ tests/
   
   # Linting
   flake8 src/ tests/
   
   # Type checking
   mypy src/
   
   # Tests
   pytest --cov=src
   ```

4. **Submit Pull Request**
   - Clear description of changes
   - Link to related issues
   - Include test results

### Code Style Guidelines

#### Python Style
- Follow PEP 8
- Use type hints for all functions
- Maximum line length: 88 characters (Black default)
- Use descriptive variable names

#### Documentation
- Docstrings for all public functions
- Type hints for parameters and return values
- Inline comments for complex logic

#### Example Function
```python
def analyze_pitcher_schedule(
    pitcher_id: str,
    start_date: date,
    end_date: date
) -> List[PitcherAnalysis]:
    """
    Analyze pitcher's schedule for the given date range.
    
    Args:
        pitcher_id: Unique identifier for the pitcher
        start_date: Start of analysis period
        end_date: End of analysis period
        
    Returns:
        List of analysis results for each potential start
        
    Raises:
        APIError: If unable to fetch schedule data
        ValidationError: If date range is invalid
    """
    if start_date >= end_date:
        raise ValidationError("Start date must be before end date")
    
    # Implementation...
    return results
```

### Commit Message Format

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Maintenance tasks

Examples:
```
feat(analysis): add second start detection logic

Implement algorithm to identify pitchers likely to get
two starts in the target period.

Closes #123
```

### Release Process

1. **Version Bump**
   ```bash
   # Update version in pyproject.toml
   git tag v1.2.0
   git push origin v1.2.0
   ```

2. **Release Notes**
   - Document new features
   - List bug fixes
   - Note breaking changes

3. **Deployment**
   - Automatic deployment via Streamlit Cloud
   - Monitor for issues
   - Rollback if necessary

---

**Happy coding! 🚀**