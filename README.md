<div align="center">
  <img src="pg_logo.png" alt="Perfect Game Logo" width="200"/>
</div>

# Perfect Game Team Scraper

A Python program that scrapes player statistics from Perfect Game team pages. Extracts comprehensive player data including batting statistics (At Bats, Batting Average, OPS, Slugging) and pitching statistics (ERA, WHIP, Strike %, Innings Pitched).

**✅ FULLY WORKING** - Successfully extracts statistics with subscription authentication!

## Quick Start

```bash
# Scrape a team
python3 pg_scraper.py "https://www.perfectgame.org/Events/Tournaments/Teams/Default.aspx?team=967917" --username "your_email" --password "your_password"

# Test a single player
python3 pg_scraper.py --test-profile "https://www.perfectgame.org/Players/Playerprofile.aspx?ID=1161417" --username "your_email" --password "your_password"
```

## Features

- Scrapes Perfect Game team pages for player statistics
- Supports authentication with Perfect Game credentials
- Extracts comprehensive baseball statistics: At Bats, Batting Average, OPS, Slugging, ERA, WHIP, Strike %, Innings Pitched
- Saves data to CSV format
- Command-line interface for easy usage
- Respectful scraping with delays and proper headers
- Comprehensive error handling and logging

## Installation

### Option 1: Automated Installation (Recommended)

1. Clone or download this repository
2. Run the installation script:

```bash
./install.sh
```

This will automatically create a virtual environment, install all dependencies including pandas and lxml, and set up the scraper.

### Option 2: Manual Installation

1. Clone or download this repository
2. Create a Python virtual environment:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

4. Make the script executable (macOS/Linux):

```bash
chmod +x pg_scraper.py
```

## Usage

### Perfect Game URL Format

The scraper works with Perfect Game tournament team URLs in this format:
```
https://www.perfectgame.org/Events/Tournaments/Teams/Default.aspx?team=TEAM_ID
```

For example: `https://www.perfectgame.org/Events/Tournaments/Teams/Default.aspx?team=967917`

### Basic Usage (without authentication)

```bash
# If using virtual environment, make sure it's activated first:
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows

python pg_scraper.py "https://www.perfectgame.org/Events/Tournaments/Teams/Default.aspx?team=967917"
```

### With Authentication

```bash
# If using virtual environment, make sure it's activated first:
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows

python pg_scraper.py "https://www.perfectgame.org/Events/Tournaments/Teams/Default.aspx?team=967917" -u your_email -p your_password
```

### Command Line Options

- `team_url`: The URL of the Perfect Game team page (required)
- `-u, --username`: Perfect Game email address for authentication (optional)
- `-p, --password`: Perfect Game password for authentication (optional)
- `-o, --output`: Output CSV filename (default: team_stats.csv)
- `-v, --verbose`: Enable verbose logging
- `-h, --help`: Show help message

### Examples

```bash
# Activate virtual environment first (if using one)
source venv/bin/activate  # On macOS/Linux

# Basic scraping without authentication
python pg_scraper.py "https://www.perfectgame.org/Events/Tournaments/Teams/Default.aspx?team=967917"

# With authentication and custom output file  
python pg_scraper.py "https://www.perfectgame.org/Events/Tournaments/Teams/Default.aspx?team=967917" -u myemail@example.com -p mypassword -o my_team_stats.csv

# With verbose logging
python pg_scraper.py "https://www.perfectgame.org/Events/Tournaments/Teams/Default.aspx?team=967917" -v
```

## Output

The program can extract different types of data depending on the page type:

### Tournament Roster Pages with Player Profile Integration
For tournament roster pages (like the example URL), the scraper now:

1. **Extracts roster information**:
   - **Name**: Player's name
   - **Height**: Player's height
   - **Weight**: Player's weight  
   - **Bats/Throws**: Batting and throwing hand (R/R, L/R, etc.)
   - **Graduation Year**: Expected graduation year
   - **School**: Current school
   - **Hometown**: Player's hometown

2. **Follows each player's profile link** to get detailed statistics:
   - **At Bats**: Number of at-bats from player profile
   - **Batting Average**: Actual batting average from player profile
   - **OPS**: On-base Plus Slugging from player profile
   - **Slugging**: Slugging percentage from player profile
   - **ERA**: Earned Run Average from player profile (for pitchers)
   - **WHIP**: Walks and Hits per Inning Pitched from player profile (for pitchers)
   - **Strike %**: Strike percentage from player profile (for pitchers)
   - **Innings Pitched**: Total innings pitched from player profile (for pitchers)

**Note**: The scraper automatically traverses each player's profile page to extract their actual batting and pitching statistics, providing comprehensive player data beyond just roster information.

### Statistics Pages
For pages with actual game statistics, the scraper extracts:
- **Name**: Player's name
- **At Bats**: Number of at-bats
- **Batting Average**: Player's batting average
- **OPS**: On-base Plus Slugging percentage
- **Slugging**: Slugging percentage
- **ERA**: Earned Run Average (for pitchers)
- **WHIP**: Walks and Hits per Inning Pitched (for pitchers)
- **Strike %**: Strike percentage (for pitchers)
- **Innings Pitched**: Total innings pitched (for pitchers)

Data is saved to a CSV file and also displayed in the terminal.

## Technical Details

### Dependencies

- `requests`: For HTTP requests and session management
- `beautifulsoup4`: For HTML parsing with lxml backend
- `pandas`: For efficient data manipulation and CSV export
- `lxml`: High-performance XML/HTML parser (required)
- `urllib3`: URL handling utilities

**Note**: Selenium is NOT required. The scraper uses pure HTTP requests with session management for authentication.

### How It Works

1. **Authentication**: If credentials are provided, the scraper attempts to log into Perfect Game
2. **Page Retrieval**: Fetches the team page using proper browser headers
3. **Roster Parsing**: Extracts player names and profile links from tournament roster tables
4. **Profile Traversal**: For each player, visits their individual profile page to get detailed statistics
5. **Statistics Extraction**: 
   - Uses advanced HTML parsing to extract statistics from specific span elements
   - Batting stats: At Bats (`ctl04_lblAB`), Batting Average (`lbl_A_PB_S_AVG`), OPS (`lbl_A_PB_S_OPS`), Slugging (`lbl_A_PB_S_SLG`)
   - Pitching stats: ERA (`ctl04_lblERA`), WHIP (`ctl04_lblWHIP`), Strike % (`ctl04_lblSPercent`), Innings Pitched (`ctl04_lblIP`)
   - Robust validation to ensure only numeric statistics are captured
   - Falls back to general table parsing for other page formats
6. **Data Integration**: Combines roster information with detailed statistics from player profiles
7. **Output**: Saves comprehensive player data to CSV and displays results

### Error Handling

- Network errors are caught and reported
- Missing data fields are marked as 'N/A'
- Invalid URLs are validated before processing
- Authentication failures are handled gracefully
- Comprehensive logging for troubleshooting

## Notes

- The scraper includes delays between requests to be respectful to the Perfect Game servers
- It uses proper browser headers to avoid being blocked
- The parsing logic is designed to handle various table formats that might be used on Perfect Game
- Authentication is optional but may be required for accessing certain team pages

## Troubleshooting

1. **Installation hangs on "building wheel"**: 
   - This typically happens with pandas or lxml packages
   - **lxml specific fix**: If lxml fails to install, try: `STATIC_DEPS=true pip3 install lxml`
   - **Alternative**: Try installing with pre-built binaries only: `pip install --only-binary=:all: -r requirements.txt`
   - **On macOS**: Install Xcode command line tools: `xcode-select --install`
   - **On Linux**: Install build essentials: `sudo apt-get install build-essential python3-dev`

2. **Virtual environment issues**: 
   - Make sure to activate the virtual environment: `source venv/bin/activate`
   - If activation fails, try recreating it: `rm -rf venv && ./install.sh`
   - Use the convenience script: `source activate.sh`

3. **Import errors**: 
   - Ensure you've activated the virtual environment before running the script
   - Verify all dependencies are installed: `pip list`
   - Both pandas and lxml are now required dependencies

4. **No data found**: Check that the URL is correct and the page contains player statistics

5. **Authentication issues**: Verify your username and password are correct

6. **Network errors**: Check your internet connection and try again

7. **Parsing errors**: Use the `-v` flag for verbose logging to see detailed information

## Legal and Ethical Considerations

- This tool is for educational and personal use only
- Respect Perfect Game's robots.txt and terms of service
- Use reasonable delays between requests
- Don't overload their servers with excessive requests
- Consider reaching out to Perfect Game for official API access for commercial use

## License

This project is for educational purposes. Please respect the terms of service of the Perfect Game website.
