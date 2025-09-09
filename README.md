# Yahoo Fantasy Baseball Analyzer

A comprehensive Streamlit application for analyzing Yahoo Fantasy Baseball leagues to find optimal Monday/Tuesday starting pitcher pickups.

![Yahoo Fantasy Baseball Analyzer](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Yahoo Fantasy API](https://img.shields.io/badge/Yahoo-Fantasy_API-7B0099?style=for-the-badge&logo=yahoo&logoColor=white)

## 🎯 Features

- **📊 Smart Analysis**: Find confirmed Monday/Tuesday starting pitchers with potential second start identification
- **🔄 Waiver Wire Intelligence**: Compare your roster against available waiver wire options with ownership data
- **📈 Advanced Statistics**: Direct links to Baseball Savant for detailed player performance metrics
- **⚡ Real-time Data**: Live integration with Yahoo Fantasy API and MLB Stats API
- **🎨 Professional UI**: Clean, responsive interface with loading indicators and error handling
- **💾 Intelligent Caching**: Optimized performance with smart data caching

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Yahoo Fantasy Sports account
- Yahoo Developer App credentials

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/yahoo-fantasy-baseball-streamlit.git
   cd yahoo-fantasy-baseball-streamlit
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure secrets**
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```
   
   Edit `.streamlit/secrets.toml` with your Yahoo API credentials (see [Configuration Guide](#-configuration-guide))

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

6. **Open your browser**
   Navigate to `http://localhost:8501`

## 🔧 Configuration Guide

### Yahoo Developer App Setup

1. **Create Yahoo Developer App**
   - Go to [Yahoo Developer Console](https://developer.yahoo.com/apps/)
   - Click "Create an App"
   - Fill in application details:
     - Application Name: "Fantasy Baseball Analyzer"
     - Application Type: "Web Application"
     - Redirect URI: `http://localhost:8080/callback`

2. **Get OAuth Credentials**
   - Note your `Client ID` and `Client Secret`
   - Follow Yahoo OAuth flow to get `Access Token` and `Refresh Token`

### Secrets Configuration

Edit `.streamlit/secrets.toml`:

```toml
[yahoo_oauth]
client_id = "your_yahoo_client_id_here"
client_secret = "your_yahoo_client_secret_here"
access_token = "your_yahoo_access_token_here"
refresh_token = "your_yahoo_refresh_token_here"

[app_config]
default_league_id = "458.l.135626"
default_team_key = "458.l.135626.t.6"
cache_ttl_seconds = 3600
max_retries = 3
request_timeout = 10

[logging]
level = "INFO"
format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

## 📋 Finding Your Team Key

Your Yahoo Fantasy team key is required to access your team data. Here's how to find it:

### Step-by-Step Instructions

1. **Go to Yahoo Fantasy Baseball**
   - Visit [fantasy.yahoo.com](https://fantasy.yahoo.com)
   - Sign in to your account

2. **Navigate to Your League**
   - Click on your Baseball league
   - Go to "My Team" page

3. **Find Team Key in URL**
   - Look at the browser address bar
   - Find the pattern: `XXX.l.XXXXXX.t.X`
   - Example: `458.l.135626.t.6`

4. **Copy the Complete Team Key**
   - Include all numbers and dots
   - Enter it in the sidebar configuration

### URL Example
```
https://baseball.fantasysports.yahoo.com/b1/458.l.135626.t.6
```
**Team Key:** `458.l.135626.t.6`

## 🎮 How to Use

### 1. Configure Your Team
- Enter your Yahoo Fantasy team key in the sidebar
- Adjust analysis settings (target days, ownership threshold, etc.)

### 2. Run Analysis
- Click "Run Analysis" to fetch current data
- View confirmed Monday/Tuesday starters
- Compare your roster vs. waiver wire options

### 3. Review Results
- **My Team Section**: Shows confirmed starters already on your roster
- **Waiver Wire Section**: Shows available starters you can pick up
- **Analysis Insights**: Key recommendations and observations

### 4. Take Action
- Click Baseball Savant links for detailed player stats
- Use recommendations to make waiver wire pickups
- Focus on players with potential second starts

## 🏗️ Architecture

### Project Structure
```
yahoo-fantasy-baseball-streamlit/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── .streamlit/
│   ├── config.toml                # Streamlit configuration
│   └── secrets.toml.example       # Secrets template
├── src/
│   ├── api/                       # API clients
│   │   ├── yahoo_client.py        # Yahoo Fantasy API
│   │   ├── mlb_client.py          # MLB Stats API
│   │   └── base_client.py         # Base API client
│   ├── core/                      # Core functionality
│   │   ├── config.py              # Configuration management
│   │   ├── constants.py           # Application constants
│   │   ├── exceptions.py          # Custom exceptions
│   │   └── logging_config.py      # Logging setup
│   ├── models/                    # Data models
│   │   ├── player.py              # Player data model
│   │   ├── team.py                # Team data model
│   │   └── analysis.py            # Analysis results model
│   ├── services/                  # Business logic
│   │   ├── analysis_service.py    # Main analysis logic
│   │   └── cache_service.py       # Caching service
│   ├── ui/                        # User interface
│   │   ├── components/            # Reusable UI components
│   │   │   ├── sidebar.py         # Sidebar configuration
│   │   │   ├── styling.py         # CSS styling
│   │   │   └── loading.py         # Loading indicators
│   │   └── pages/                 # Page components
│   │       ├── analysis_tab.py    # Analysis results page
│   │       └── roster_tab.py      # Roster management page
│   └── utils/                     # Utility functions
│       ├── date_utils.py          # Date handling
│       ├── text_utils.py          # Text processing
│       └── url_utils.py           # URL utilities
└── tests/                         # Test files
    └── __init__.py
```

### Key Components

- **API Layer**: Handles communication with Yahoo Fantasy and MLB Stats APIs
- **Service Layer**: Contains business logic for analysis and caching
- **UI Layer**: Streamlit components for user interface
- **Models**: Pydantic models for data validation and structure
- **Configuration**: Centralized configuration management with validation

## 🔌 API Integration

### Yahoo Fantasy API
- **Authentication**: OAuth 2.0 with refresh token support
- **Endpoints**: Team roster, league settings, player ownership
- **Rate Limiting**: Built-in retry logic with exponential backoff

### MLB Stats API
- **Data Source**: Official MLB statistics and probable pitchers
- **Endpoints**: Schedule, probable pitchers, player stats
- **Caching**: Intelligent caching to minimize API calls

## 🧪 Testing

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/

# Run with coverage
pytest --cov=src tests/
```

### Test Coverage
- Unit tests for core functionality
- Integration tests for API clients
- UI component testing
- Error handling validation

## 🚀 Deployment

### Streamlit Cloud Deployment

1. **Prepare Repository**
   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

2. **Deploy to Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Select the main branch
   - Set the main file path: `app.py`

3. **Configure Secrets**
   - In Streamlit Cloud dashboard, go to "Secrets"
   - Copy contents from your local `.streamlit/secrets.toml`
   - Save the secrets configuration

4. **Monitor Deployment**
   - Check deployment logs for any issues
   - Verify application functionality
   - Test with real Yahoo Fantasy data

### Environment Variables

For production deployment, set these environment variables:

```bash
YAHOO_CLIENT_ID=your_client_id
YAHOO_CLIENT_SECRET=your_client_secret
YAHOO_ACCESS_TOKEN=your_access_token
YAHOO_REFRESH_TOKEN=your_refresh_token
```

## 🔧 Troubleshooting

### Common Issues

#### Configuration Errors
```
⚠️ Configuration error: Failed to load configuration
```
**Solution**: Check your `.streamlit/secrets.toml` file and ensure all required fields are filled.

#### Invalid Team Key Format
```
❌ Invalid team key format
```
**Solution**: Ensure your team key follows the pattern `XXX.l.XXXXXX.t.X` (e.g., `458.l.135626.t.6`).

#### API Connection Issues
```
❌ API error: Connection timeout
```
**Solutions**:
- Check your internet connection
- Verify Yahoo API credentials are valid
- Try refreshing your OAuth tokens

#### No Data Returned
```
No confirmed Monday/Tuesday starters found
```
**Solutions**:
- Verify your team key is correct
- Ensure you have players on your roster
- Check if it's the current baseball season

### Debug Mode

Enable debug logging by updating your secrets:
```toml
[logging]
level = "DEBUG"
```

## 📊 Performance Optimization

### Caching Strategy
- **API Responses**: Cached for 1 hour (configurable)
- **Player Data**: Cached per session
- **Analysis Results**: Cached until manual refresh

### Memory Management
- Efficient data structures using Pandas
- Lazy loading of non-essential data
- Automatic cleanup of expired cache entries

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Install development dependencies: `pip install -r requirements-dev.txt`
4. Make your changes
5. Run tests: `pytest`
6. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Use type hints for all functions
- Add docstrings for public methods
- Maintain test coverage above 80%

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Yahoo Fantasy API** for providing comprehensive fantasy sports data
- **MLB Stats API** for official baseball statistics
- **Streamlit** for the excellent web app framework
- **Baseball Savant** for advanced player analytics

## 📞 Support

- **Documentation**: Check this README and inline help
- **Issues**: Report bugs on [GitHub Issues](https://github.com/yourusername/yahoo-fantasy-baseball-streamlit/issues)
- **Discussions**: Join conversations on [GitHub Discussions](https://github.com/yourusername/yahoo-fantasy-baseball-streamlit/discussions)

---

**Built with ❤️ for fantasy baseball enthusiasts**