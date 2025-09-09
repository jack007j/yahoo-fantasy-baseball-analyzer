# Yahoo Fantasy Baseball Analyzer - User Guide

A comprehensive guide to using the Yahoo Fantasy Baseball Analyzer for optimal Monday/Tuesday starter pickups.

## 📚 Table of Contents

1. [Getting Started](#getting-started)
2. [Finding Your Team Key](#finding-your-team-key)
3. [Configuration Settings](#configuration-settings)
4. [Running Analysis](#running-analysis)
5. [Understanding Results](#understanding-results)
6. [Advanced Features](#advanced-features)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

## 🚀 Getting Started

### First Time Setup

1. **Access the Application**
   - Open your web browser
   - Navigate to the application URL (local: `http://localhost:8501`)
   - You'll see the welcome screen with configuration instructions

2. **Initial Configuration Required**
   - The app requires your Yahoo Fantasy team key to function
   - You'll see a message: "Configure your team settings in the sidebar to get started"
   - All analysis features are disabled until configuration is complete

### Application Layout

The application consists of three main areas:

- **Header**: Application title and description
- **Sidebar**: Configuration panel (left side)
- **Main Area**: Analysis results and tabs (center/right)

## 🔑 Finding Your Team Key

Your Yahoo Fantasy team key is a unique identifier that allows the app to access your team data.

### Step-by-Step Instructions

#### Method 1: From Yahoo Fantasy Website

1. **Login to Yahoo Fantasy**
   ```
   https://fantasy.yahoo.com
   ```

2. **Navigate to Your Baseball League**
   - Click on "Fantasy Baseball" if not already selected
   - Select your specific league from the list

3. **Go to Your Team Page**
   - Click "My Team" in the navigation menu
   - This takes you to your team's roster page

4. **Extract Team Key from URL**
   - Look at the browser address bar
   - The URL will look like:
   ```
   https://baseball.fantasysports.yahoo.com/b1/458.l.135626.t.6/team
   ```
   - Your team key is: `458.l.135626.t.6`

#### Method 2: From League Homepage

1. **Go to League Homepage**
   - From your team page, click "League" tab
   - Click on your team name in the standings

2. **Check URL Pattern**
   - The URL will contain your team key
   - Format: `XXX.l.XXXXXX.t.X`

### Team Key Format

- **Game Code**: First number (e.g., `458` for baseball)
- **League ID**: Middle number after `.l.` (e.g., `135626`)
- **Team ID**: Last number after `.t.` (e.g., `6`)

**Complete Format**: `458.l.135626.t.6`

### Common Mistakes

❌ **Incorrect**: `458.l.135626` (missing team ID)
❌ **Incorrect**: `135626.t.6` (missing game code and league separator)
❌ **Incorrect**: `458-l-135626-t-6` (using dashes instead of dots)
✅ **Correct**: `458.l.135626.t.6`

## ⚙️ Configuration Settings

### Team Configuration

#### Yahoo Fantasy Team Key
- **Purpose**: Identifies your specific team for data retrieval
- **Format**: `XXX.l.XXXXXX.t.X`
- **Validation**: Real-time format checking with visual feedback
- **Status Indicators**:
  - ✅ Green checkmark: Valid format
  - ❌ Red X: Invalid format with helpful error message

### Analysis Settings

#### Target Days for Analysis
- **Default**: Monday and Tuesday
- **Options**: Any combination of weekdays
- **Purpose**: Determines which days to analyze for starting pitchers
- **Recommendation**: Keep Monday/Tuesday for optimal two-start potential

#### Minimum Ownership Percentage
- **Range**: 0% to 100%
- **Default**: 0% (show all players)
- **Purpose**: Filter out highly owned players
- **Use Cases**:
  - `0%`: See all available players
  - `50%`: Focus on widely available players
  - `75%`: Find deep sleepers

#### Analyze Potential Second Starts
- **Default**: Enabled
- **Purpose**: Identify pitchers likely to get two starts in the week
- **Impact**: Highlights high-value pickup opportunities

#### Include Waiver Wire Players
- **Default**: Enabled
- **Purpose**: Show available players not on your roster
- **When to Disable**: If you only want to see your current players

## 🔍 Running Analysis

### Starting Analysis

1. **Ensure Configuration is Complete**
   - Valid team key entered
   - Settings adjusted to your preferences

2. **Click "Run Analysis"**
   - Blue button in the main area
   - Analysis typically takes 10-30 seconds
   - Progress indicator shows current status

3. **Wait for Results**
   - Loading spinner indicates processing
   - Success message confirms completion
   - Results automatically display below

### Analysis Process

The application performs these steps:

1. **Fetch Team Data**: Retrieves your current roster from Yahoo
2. **Get League Settings**: Obtains league configuration and rules
3. **Retrieve MLB Schedule**: Gets upcoming games and probable pitchers
4. **Calculate Ownership**: Determines player ownership percentages
5. **Identify Opportunities**: Finds optimal pickup candidates
6. **Generate Insights**: Creates actionable recommendations

### Cache Management

- **Automatic Caching**: Results cached for 1 hour by default
- **Manual Refresh**: Click "Clear Cache" to force new data
- **When to Clear Cache**:
  - After making roster moves
  - When probable pitchers change
  - If data seems outdated

## 📊 Understanding Results

### Fantasy Week Header

Displays key information about the analysis period:

- **Week Display**: Date range being analyzed
- **Week Number**: Fantasy week number
- **Target Days**: Days included in analysis
- **Analysis Time**: How long the analysis took
- **Total Found**: Number of pitchers analyzed

### Summary Metrics

Four key metrics displayed in columns:

#### My Team Pitchers
- **Definition**: Confirmed starters already on your roster
- **Action**: No pickup required, just start them
- **Strategy**: Verify they're in your starting lineup

#### Waiver Options
- **Definition**: Available starters you can pick up
- **Action**: Consider adding to your roster
- **Priority**: Focus on highest-ranked options

#### Potential 2nd Starts
- **Definition**: Pitchers likely to start twice in the period
- **Value**: Double the potential points
- **Strategy**: Prioritize these pickups

#### Mon/Tue Split
- **Format**: `X/Y` (Monday starters / Tuesday starters)
- **Purpose**: Shows distribution across target days
- **Strategy**: Balance your pickups across both days

### Player Results Tables

#### My Team Section
Shows pitchers already on your roster:

- **Player**: Name and positions
- **MLB Team**: Current team
- **Start Date**: Confirmed start date
- **Ownership**: League ownership percentage
- **Potential 2nd**: Likelihood of second start
- **Notes**: Specific recommendations
- **Savant Link**: Direct link to advanced stats

#### Waiver Wire Section
Shows available pickup options:

- **Same columns as My Team**
- **Sorted by priority/value**
- **Focus on low ownership, high upside**

### Analysis Insights

Automated observations and recommendations:

- **Second Start Opportunities**: Players with multiple start potential
- **Low-Owned Options**: Hidden gems with low ownership
- **Roster vs. Waiver Comparison**: Strategic pickup advice
- **Specific Recommendations**: Actionable next steps

## 🔧 Advanced Features

### Detailed Player Cards

Click "Detailed View" expander for enhanced information:

- **Complete player profiles**
- **Recent performance trends**
- **Matchup analysis**
- **Historical data**

### Baseball Savant Integration

Direct links to Baseball Savant provide:

- **Advanced metrics** (xERA, xFIP, etc.)
- **Pitch arsenal analysis**
- **Recent performance trends**
- **Ballpark factors**

### Export Functionality

- **Copy player names** for easy roster management
- **Save analysis results** for later reference
- **Share insights** with league mates

## 🔧 Troubleshooting

### Common Issues and Solutions

#### "Configuration Required" Message

**Problem**: App shows welcome screen instead of analysis
**Cause**: Team key not entered or invalid format
**Solution**:
1. Enter your complete team key in sidebar
2. Verify format: `XXX.l.XXXXXX.t.X`
3. Check for typos or missing characters

#### "Invalid Team Key Format" Error

**Problem**: Red error message below team key input
**Cause**: Team key doesn't match expected pattern
**Solution**:
1. Double-check the format from Yahoo URL
2. Ensure all dots are included
3. Verify no extra spaces or characters

#### "No Data Returned" Results

**Problem**: Analysis completes but shows no pitchers
**Possible Causes**:
- Off-season (no games scheduled)
- No probable pitchers announced yet
- All target day games already played
- Very restrictive filter settings

**Solutions**:
1. Check if it's baseball season
2. Adjust target days to include more options
3. Lower ownership threshold
4. Wait for probable pitchers to be announced

#### API Connection Errors

**Problem**: "API error" or timeout messages
**Causes**:
- Internet connectivity issues
- Yahoo API temporarily down
- Rate limiting

**Solutions**:
1. Check internet connection
2. Wait a few minutes and retry
3. Clear cache and try again
4. Contact support if persistent

#### Slow Performance

**Problem**: Analysis takes very long or times out
**Causes**:
- Large league with many players
- Network connectivity issues
- Server overload

**Solutions**:
1. Check internet speed
2. Try during off-peak hours
3. Clear browser cache
4. Restart the application

### Getting Help

#### Built-in Help
- **Hover tooltips**: Hover over (?) icons for explanations
- **Expandable sections**: Click "How to Find Your Team Key" for guidance
- **Error messages**: Specific guidance for each error type

#### External Resources
- **Yahoo Fantasy Help**: [help.yahoo.com/kb/fantasy](https://help.yahoo.com/kb/fantasy)
- **MLB Schedule**: [mlb.com/schedule](https://mlb.com/schedule)
- **Baseball Savant**: [baseballsavant.mlb.com](https://baseballsavant.mlb.com)

## 💡 Best Practices

### Optimal Usage Patterns

#### Weekly Routine
1. **Sunday Evening**: Run analysis for upcoming week
2. **Monday Morning**: Make waiver claims based on results
3. **Tuesday**: Verify lineups include recommended starters
4. **Mid-week**: Re-run if probable pitchers change

#### Strategic Considerations

##### Prioritize Two-Start Pitchers
- **Higher point potential**: Double the opportunities
- **Competitive advantage**: Often overlooked by casual players
- **Risk management**: One bad start offset by another

##### Consider Matchup Quality
- **Opponent strength**: Weak offenses = better opportunities
- **Ballpark factors**: Pitcher-friendly parks boost performance
- **Weather conditions**: Wind and temperature affect outcomes

##### Balance Risk vs. Reward
- **High-floor options**: Reliable veterans for consistent points
- **High-ceiling picks**: Young players with breakout potential
- **Streaming strategy**: Different approaches for different weeks

#### League-Specific Strategies

##### Deep Leagues (12+ teams)
- **Lower ownership thresholds**: More players are rostered
- **Focus on matchups**: Quality becomes more important
- **Handcuff strategy**: Roster backup options

##### Shallow Leagues (8-10 teams)
- **Higher standards**: Only elite options worth rostering
- **Streaming focus**: Constantly churn for best matchups
- **Injury replacements**: Quick pivots when starters get hurt

### Data Interpretation Tips

#### Ownership Percentages
- **0-25%**: Deep sleepers, high risk/reward
- **25-50%**: Solid options, moderate risk
- **50-75%**: Popular picks, lower upside
- **75%+**: Widely owned, limited availability

#### Second Start Probability
- **"Likely"**: High confidence, prioritize these
- **"Possible"**: Monitor for confirmation
- **"Unlikely"**: Single start expected

#### Recommendation Priorities
1. **Two-start pitchers with good matchups**
2. **Single-start aces against weak opponents**
3. **Streaming options in pitcher-friendly parks**
4. **Injury replacements for roster stability**

---

**Happy analyzing! May your Monday/Tuesday starters dominate the competition! ⚾**