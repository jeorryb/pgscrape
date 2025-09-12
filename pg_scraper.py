#!/usr/bin/env python3
"""
Perfect Game Team Scraper

A comprehensive scraper for extracting player statistics from Perfect Game team pages.
Extracts batting and pitching statistics along with player demographic information.
"""

import argparse
import logging
import re
import sys
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

# pandas is now required for CSV handling
import pandas as pd

class PerfectGameScraper:
    """
    Perfect Game team scraper with comprehensive statistics extraction.
    
    Extracts player demographics from team roster tables and detailed
    batting/pitching statistics from individual player profiles.
    """
    
    def __init__(self, username=None, password=None):
        """Initialize the scraper with optional credentials."""
        self.session = requests.Session()
        self.username = username
        self.password = password
        self.base_url = "https://www.perfectgame.org"
        
        # Set up headers to mimic a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Set up logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
    
    def authenticate(self):
        """Authenticate with Perfect Game using session-based login."""
        if not self.username or not self.password:
            self.logger.info("No credentials provided, proceeding without authentication")
            return True
        
        try:
            self.logger.info("🔐 Starting authentication...")
            
            # Step 1: Get the sign-in page
            login_url = "https://www.perfectgame.org/mypg/signin.aspx"
            response = self.session.get(login_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Step 2: Find the login form (use first form)
            forms = soup.find_all('form')
            if not forms:
                self.logger.warning("No forms found on sign-in page")
                return False
            
            login_form = forms[0]
            
            # Step 3: Extract all form data
            form_data = {}
            all_inputs = login_form.find_all('input')
            
            for input_field in all_inputs:
                name = input_field.get('name')
                value = input_field.get('value', '')
                if name:
                    form_data[name] = value
            
            # Step 4: Set credentials using the exact field names that worked
            email_field_name = 'ctl00$ctl00$ContentTopLevel$ContentPlaceHolder1$tbUserEmail'
            password_field_name = 'ctl00$ctl00$ContentTopLevel$ContentPlaceHolder1$tbUserSecret'
            
            form_data[email_field_name] = self.username
            form_data[password_field_name] = self.password
            
            self.logger.info(f"📝 Submitting login with {len(form_data)} form fields")
            
            # Step 5: Submit login form
            login_response = self.session.post(login_url, data=form_data)
            login_response.raise_for_status()
            
            # Step 6: Check authentication success
            response_text_lower = login_response.text.lower()
            success_indicators = ['sign out', 'logout', 'my account', 'welcome']
            
            login_successful = any(indicator in response_text_lower for indicator in success_indicators)
            
            if login_successful:
                self.logger.info("✅ Authentication successful!")
                return True
            else:
                self.logger.warning("⚠️ Authentication status unclear")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Authentication failed: {e}")
            return False
    
    def _find_roster_table_players(self, soup):
        """
        Extract player information from the team roster table.
        
        Returns dictionary mapping profile URLs to player data including
        name, school, hometown, physical stats, etc.
        """
        try:
            # Look for tables that have roster-like structure
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                if len(rows) < 2:  # Need at least header + 1 data row
                    continue
                
                # Check if this looks like a roster table
                header_row = rows[0]
                header_cells = header_row.find_all(['th', 'td'])
                header_texts = [cell.get_text(strip=True).lower() for cell in header_cells]
                
                # Look for roster table indicators in headers
                roster_indicators = ['name', 'ht', 'wt', 'b/t', 'no.', 'pos']
                if any(indicator in ' '.join(header_texts) for indicator in roster_indicators):
                    self.logger.info(f"📋 Found roster table with headers: {header_texts}")
                    
                    # Extract players from this table
                    roster_players = {}
                    
                    # Map header positions for data extraction
                    header_map = {}
                    for i, header in enumerate(header_texts):
                        header_map[header] = i
                    
                    for row in rows[1:]:  # Skip header row
                        cells = row.find_all(['td', 'th'])
                        if len(cells) < 2:  # Need at least 2 cells for meaningful data
                            continue
                        
                        # Look for player links in this row
                        player_links = row.find_all('a', href=lambda x: x and ('PlayerProfile.aspx' in x or 'Playerprofile.aspx' in x))
                        
                        for link in player_links:
                            href = link.get('href')
                            player_name = link.get_text(strip=True)
                            
                            if href and player_name and len(player_name) > 2:
                                # Make URL absolute
                                if href.startswith('/'):
                                    profile_url = f"{self.base_url}{href}"
                                elif href.startswith('http'):
                                    profile_url = href
                                else:
                                    profile_url = f"{self.base_url}/{href}"
                                
                                # Extract just the player name (remove position info)
                                clean_name = player_name.split('OF')[0].split('C,')[0].split('RHP')[0].split('SS')[0].split('UTL')[0].split('Last')[0].strip()
                                
                                if clean_name:
                                    # Extract additional roster data from the table
                                    player_roster_data = {
                                        'name': clean_name,
                                        'profile_url': profile_url
                                    }
                                    
                                    # Extract school if available
                                    if 'school' in header_map and header_map['school'] < len(cells):
                                        school = cells[header_map['school']].get_text(strip=True)
                                        if school and school != '-' and school != 'N/A':
                                            player_roster_data['school'] = school
                                    
                                    # Extract hometown if available
                                    if 'hometown' in header_map and header_map['hometown'] < len(cells):
                                        hometown = cells[header_map['hometown']].get_text(strip=True)
                                        if hometown and hometown != '-' and hometown != 'N/A':
                                            player_roster_data['hometown'] = hometown
                                    
                                    # Extract height if available
                                    if 'ht' in header_map and header_map['ht'] < len(cells):
                                        height = cells[header_map['ht']].get_text(strip=True)
                                        if height and height != '-' and height != 'N/A':
                                            player_roster_data['height'] = height
                                    
                                    # Extract weight if available
                                    if 'wt' in header_map and header_map['wt'] < len(cells):
                                        weight = cells[header_map['wt']].get_text(strip=True)
                                        if weight and weight != '-' and weight != 'N/A':
                                            player_roster_data['weight'] = weight
                                    
                                    # Extract bats/throws if available
                                    if 'b/t' in header_map and header_map['b/t'] < len(cells):
                                        bats_throws = cells[header_map['b/t']].get_text(strip=True)
                                        if bats_throws and bats_throws != '-' and bats_throws != 'N/A':
                                            player_roster_data['bats_throws'] = bats_throws
                                    
                                    # Extract graduation year if available
                                    if 'grad' in header_map and header_map['grad'] < len(cells):
                                        grad_year = cells[header_map['grad']].get_text(strip=True)
                                        if grad_year and grad_year != '-' and grad_year != 'N/A':
                                            player_roster_data['grad_year'] = grad_year
                                    
                                    roster_players[profile_url] = player_roster_data
                                    self.logger.info(f"🏃 Found roster player: {clean_name}")
                    
                    if roster_players:
                        return roster_players
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding roster table players: {e}")
            return None
    
    def scrape_team(self, team_url):
        """Scrape team page and extract player data."""
        try:
            # Authenticate first
            if not self.authenticate():
                self.logger.error("Authentication failed, cannot proceed")
                return []
            
            self.logger.info(f"🏆 Fetching team page: {team_url}")
            response = self.session.get(team_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            players = []
            
            # Look for the actual team roster table
            roster_players = self._find_roster_table_players(soup)
            
            if roster_players:
                self.logger.info(f"🔍 Found {len(roster_players)} players in roster table")
                unique_players = roster_players
            else:
                # Fallback to the old method if roster table not found
                self.logger.warning("Roster table not found, falling back to general player link search")
                player_links = []
                
                # Look for links containing PlayerProfile or Playerprofile
                profile_links = soup.find_all('a', href=lambda x: x and ('PlayerProfile.aspx' in x or 'Playerprofile.aspx' in x))
                player_links.extend(profile_links)
                
                self.logger.info(f"🔍 Found {len(player_links)} potential player links")
                
                # Extract unique player URLs and names
                unique_players = {}
                for link in player_links:
                    href = link.get('href')
                    if href:
                        # Make URL absolute
                        if href.startswith('/'):
                            profile_url = f"{self.base_url}{href}"
                        elif href.startswith('http'):
                            profile_url = href
                        else:
                            profile_url = f"{self.base_url}/{href}"
                        
                        # Get player name from link text
                        player_name = link.get_text(strip=True)
                        
                        # Only process if we have a valid name and URL
                        if player_name and len(player_name) > 2 and 'ID=' in profile_url:
                            unique_players[profile_url] = player_name
            
            self.logger.info(f"👥 Processing {len(unique_players)} unique players")
            
            # Process each player
            for i, (profile_url, player_info) in enumerate(unique_players.items(), 1):
                # Handle both old format (string) and new format (dict)
                if isinstance(player_info, dict):
                    player_name = player_info['name']
                    roster_data = player_info
                else:
                    player_name = player_info
                    roster_data = {'name': player_info}
                
                self.logger.info(f"🏃 Processing player {i}/{len(unique_players)}: {player_name}")
                
                try:
                    player_data = self.get_player_profile_data(profile_url)
                    
                    # Merge roster data with profile data, giving priority to roster data for basic info
                    if player_data:
                        # Update with roster data (school, hometown, etc. from team page)
                        if 'school' in roster_data:
                            player_data['School'] = roster_data['school']
                        if 'hometown' in roster_data:
                            player_data['Hometown'] = roster_data['hometown']
                        if 'height' in roster_data:
                            player_data['Height'] = roster_data['height']
                        if 'weight' in roster_data:
                            player_data['Weight'] = roster_data['weight']
                        if 'bats_throws' in roster_data:
                            player_data['Bats/Throws'] = roster_data['bats_throws']
                        if 'grad_year' in roster_data:
                            player_data['Graduation Year'] = roster_data['grad_year']
                        
                        players.append(player_data)
                    
                    # Add delay to be respectful to the server
                    if i < len(unique_players):  # Don't delay after the last player
                        time.sleep(1)
                        
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to process {player_name}: {e}")
                    continue
            
            self.logger.info(f"✅ Successfully processed {len(players)} players")
            return players
            
        except Exception as e:
            self.logger.error(f"❌ Error scraping team: {e}")
            return []
    
    def get_player_profile_data(self, profile_url):
        """Extract player data from profile page."""
        try:
            self.logger.info(f"🔍 Fetching player profile: {profile_url}")
            
            # Get the profile page
            response = self.session.get(profile_url)
            response.raise_for_status()
            
            self.logger.debug(f"📊 Profile HTML length: {len(response.text)} characters")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            player_data = {
                'Name': 'N/A',
                'Height': 'N/A',
                'Weight': 'N/A',
                'Bats/Throws': 'N/A',
                'Graduation Year': 'N/A',
                'School': 'N/A',
                'Hometown': 'N/A',
                'Batting Average': 'N/A',
                'OPS': 'N/A',
                'Slugging': 'N/A',
                'ERA': 'N/A',
                'Innings Pitched': 'N/A'
            }
            
            # Extract basic player info
            self._extract_player_info(soup, player_data)
            
            # Extract statistics
            self._extract_statistics(soup, player_data)
            
            return player_data
            
        except Exception as e:
            self.logger.error(f"Error processing player profile {profile_url}: {e}")
            return None
    
    def _extract_player_info(self, soup, player_data):
        """Extract basic player information."""
        try:
            # Player name
            name_span = soup.find('span', {'id': 'ContentTopLevel_ContentPlaceHolder1_lblPlayerName'})
            if name_span:
                player_data['Name'] = name_span.get_text(strip=True)
                self.logger.info(f"✅ Name: {player_data['Name']}")
            
            # Height
            height_span = soup.find('span', {'id': 'ContentTopLevel_ContentPlaceHolder1_lblHt'})
            if height_span:
                player_data['Height'] = height_span.get_text(strip=True)
                self.logger.info(f"✅ Height: {player_data['Height']}")
            
            # Weight
            weight_span = soup.find('span', {'id': 'ContentTopLevel_ContentPlaceHolder1_lblWt'})
            if weight_span:
                weight_text = weight_span.get_text(strip=True).strip().lstrip('\u00a0').strip()
                if weight_text:
                    player_data['Weight'] = weight_text
                    self.logger.info(f"✅ Weight: {player_data['Weight']}")
            
            # Bats/Throws
            bt_span = soup.find('span', {'id': 'ContentTopLevel_ContentPlaceHolder1_lblBT'})
            if bt_span:
                player_data['Bats/Throws'] = bt_span.get_text(strip=True)
                self.logger.info(f"✅ Bats/Throws: {player_data['Bats/Throws']}")
            
            # Graduation year
            grad_span = soup.find('span', {'id': 'ContentTopLevel_ContentPlaceHolder1_lblHSGrad'})
            if grad_span:
                grad_text = grad_span.get_text(strip=True)
                year_match = re.search(r'(\d{4})', grad_text)
                if year_match:
                    player_data['Graduation Year'] = year_match.group(1)
                    self.logger.info(f"✅ Graduation Year: {player_data['Graduation Year']}")
            
        except Exception as e:
            self.logger.warning(f"Error extracting player info: {e}")
    
    def _extract_statistics(self, soup, player_data):
        """Extract statistics from the page."""
        try:
            self.logger.info("🔍 Extracting statistics...")
            
            # Define statistics to extract with their span patterns
            stat_patterns = {
                'OPS': lambda x: x and x.endswith('_ctl04_lbl_A_PB_S_OPS'),
                'Batting Average': lambda x: x and x.endswith('_ctl04_lbl_A_PB_S_AVG'),
                'Slugging': lambda x: x and x.endswith('_ctl04_lbl_A_PB_S_SLG'),
                'At Bats': lambda x: x and 'ctl04_lblAB' in x,
                'ERA': lambda x: x and 'ctl04_lblERA' in x,
                'Innings Pitched': lambda x: x and 'ctl04_lblIP' in x,
                'WHIP': lambda x: x and 'ctl04_lblWHIP' in x,
                'Strike %': lambda x: x and 'ctl04_lblSPercent' in x
            }
            
            stats_found = 0
            
            # Extract all statistics using the defined patterns
            for stat_name, pattern_func in stat_patterns.items():
                span = soup.find('span', {'id': pattern_func})
                if span:
                    value = span.get_text(strip=True)
                    if self._is_valid_stat(value):
                        player_data[stat_name] = value
                        self.logger.info(f"✅ {stat_name}: {value}")
                        stats_found += 1
            
            if stats_found > 0:
                self.logger.info(f"✅ Found {stats_found} advanced statistics")
            else:
                self.logger.warning("❌ No advanced statistics found")
            
        except Exception as e:
            self.logger.error(f"Error extracting statistics: {e}")
    
    def _is_valid_stat(self, value):
        """Check if a value is a valid numeric statistic."""
        if not value or len(value.strip()) == 0:
            return False
        
        value = value.strip()
        
        # Check for invalid keywords
        invalid_keywords = ['subscribe', 'n/a', 'error', 'null', 'undefined', 'nan']
        if any(keyword in value.lower() for keyword in invalid_keywords):
            return False
        
        # Check if it's too long (subscription text is usually very long)
        if len(value) > 10:
            return False
        
        # Check if it looks like a valid number
        if re.match(r'^\.?\d+\.?\d*$', value):
            return True
        
        return False
    
    def save_to_csv(self, players, filename):
        """Save player data to CSV file with optimized column ordering."""
        try:
            if not players:
                self.logger.warning("No player data to save")
                return
            
            # Create DataFrame from player data
            df = pd.DataFrame(players)
            
            # Define preferred column order with Name first
            preferred_order = [
                'Name', 'Height', 'Weight', 'Bats/Throws', 'Graduation Year',
                'School', 'Hometown', 'At Bats', 'Batting Average', 'OPS', 'Slugging', 
                'ERA', 'WHIP', 'Strike %', 'Innings Pitched'
            ]
            
            # Reorder columns: preferred fields first, then any additional fields
            existing_cols = df.columns.tolist()
            ordered_cols = [col for col in preferred_order if col in existing_cols]
            remaining_cols = sorted([col for col in existing_cols if col not in preferred_order])
            final_cols = ordered_cols + remaining_cols
            
            # Apply column ordering and save to CSV
            df = df[final_cols]
            df.to_csv(filename, index=False)
            self.logger.info(f"💾 Data saved to {filename}")
                
        except Exception as e:
            self.logger.error(f"Error saving to CSV: {e}")

def main():
    """Main function to run the scraper from command line."""
    parser = argparse.ArgumentParser(description='Perfect Game scraper with working authentication')
    parser.add_argument('team_url', nargs='?', help='Perfect Game team URL')
    parser.add_argument('--test-profile', help='Test with a single player profile URL')
    parser.add_argument('-u', '--username', help='Perfect Game username')
    parser.add_argument('-p', '--password', help='Perfect Game password')
    parser.add_argument('-o', '--output', default='team_stats.csv', help='Output CSV filename')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate arguments
    if not args.test_profile and not args.team_url:
        print("❌ Please provide either a team URL or --test-profile URL")
        print("\nExamples:")
        print("  Team scraping:")
        print("    python3 working_scraper.py 'https://www.perfectgame.org/Events/Tournaments/Teams/Default.aspx?team=967917' --username 'email' --password 'pass'")
        print("  Single player test:")
        print("    python3 working_scraper.py --test-profile 'https://www.perfectgame.org/Players/Playerprofile.aspx?ID=1161417' --username 'email' --password 'pass'")
        sys.exit(1)
    
    try:
        scraper = PerfectGameScraper(username=args.username, password=args.password)
        
        # Test profile mode
        if args.test_profile:
            print("🧪 TESTING SINGLE PLAYER PROFILE")
            print("="*60)
            
            if scraper.authenticate():
                player_data = scraper.get_player_profile_data(args.test_profile)
                
                if player_data:
                    print("\n🏆 PLAYER PROFILE RESULTS")
                    print("="*60)
                    
                    for key, value in player_data.items():
                        status = "✅" if value != 'N/A' else "❌"
                        print(f"{status} {key}: {value}")
                    
                    # Count successful extractions
                    successful = sum(1 for v in player_data.values() if v != 'N/A')
                    total = len(player_data)
                    print(f"\n📊 Successfully extracted {successful}/{total} data points")
                    
                else:
                    print("❌ No player data found")
            else:
                print("❌ Authentication failed")
        
        # Team scraping mode
        elif args.team_url:
            print("🏆 SCRAPING TEAM DATA")
            print("="*60)
            
            players = scraper.scrape_team(args.team_url)
            
            if players:
                # Save to CSV
                scraper.save_to_csv(players, args.output)
                
                print(f"\n✅ Successfully scraped {len(players)} players!")
                print("="*60)
                
                # Show summary statistics
                stats_summary = {}
                for player in players:
                    for key, value in player.items():
                        if value != 'N/A':
                            stats_summary[key] = stats_summary.get(key, 0) + 1
                
                print("\n📊 DATA SUMMARY:")
                for stat, count in sorted(stats_summary.items()):
                    percentage = (count / len(players)) * 100
                    print(f"  ✅ {stat}: {count}/{len(players)} players ({percentage:.1f}%)")
                
                # Show first few players as examples
                print(f"\n👥 SAMPLE PLAYERS (first 3):")
                for i, player in enumerate(players[:3], 1):
                    print(f"\n  Player {i}: {player.get('Name', 'Unknown')}")
                    key_stats = ['Height', 'Weight', 'Bats/Throws', 'Graduation Year', 'Batting Average', 'OPS', 'Slugging']
                    for stat in key_stats:
                        value = player.get(stat, 'N/A')
                        if value != 'N/A':
                            print(f"    {stat}: {value}")
                
                print(f"\n💾 Full data saved to: {args.output}")
                
            else:
                print("❌ No player data found. Please check the team URL and try again.")
                sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Scraping interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print("\nFull error details:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
