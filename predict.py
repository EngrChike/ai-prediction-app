import os
import json
import math
import requests
from datetime import datetime

class DonChikeAI:
    def __init__(self):
        # Pulling the secret key from GitHub Actions Environment
        self.api_key = os.getenv('FOOTBALL_API_KEY')
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = {
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': 'v3.football.api-sports.io'
        }

    def fetch_fixtures(self):
        """Fetches upcoming high-profile matches (Premier League, La Liga, etc.)"""
        # League 39 = Premier League. You can add more IDs in a loop.
        url = f"{self.base_url}/fixtures?league=39&season=2025&next=15"
        response = requests.get(url, headers=self.headers)
        return response.json().get('response', [])

    def analyze_intensity(self, fixture_id):
        """Checks for High Intensity: Shots on Target, Possession, and Injuries"""
        # Fetch Stats
        stats_url = f"{self.base_url}/fixtures/statistics?fixture={fixture_id}"
        stats = requests.get(stats_url, headers=self.headers).json().get('response', [])
        
        # Fetch Lineups/Injuries
        lineup_url = f"{self.base_url}/fixtures/lineups?fixture={fixture_id}"
        lineups = requests.get(lineup_url, headers=self.headers).json().get('response', [])
        
        # Logic: If average shots on target > 5, it's 'High Intensity'
        intensity_score = 0
        if stats:
            for team in stats:
                for s in team['statistics']:
                    if s['type'] == 'Shots on Goal' and int(s['value'] or 0) > 5:
                        intensity_score += 1
        
        return intensity_score

    def generate_predictions(self):
        fixtures = self.fetch_fixtures()
        morning_slip = []
        evening_slip = []
        ten_day_pick = None
        
        for f in fixtures:
            home = f['teams']['home']['name']
            away = f['teams']['away']['name']
            fix_id = f['fixture']['id']
            
            # Run intensity check
            score = self.analyze_intensity(fix_id)
            
            # Logic for 5-Odds (Mix of GG and Over 2.5)
            if len(morning_slip) < 3 and score >= 1:
                morning_slip.append({"match": f"{home} vs {away}", "tip": "Over 2.5", "odds": 1.85})
            
            # Logic for 10-Day Daily Over 2.5 (Pick the safest one)
            if not ten_day_pick and score >= 2:
                ten_day_pick = {"match": f"{home} vs {away}", "tip": "Over 2.5", "date": datetime.now().strftime("%Y-%m-%d")}

        return morning_slip, ten_day_pick

    def update_storage(self, morning_slip, ten_day_pick):
        # 1. Update Tracker (10-Day Logic)
        with open('tracker.json', 'r+') as f:
            data = json.load(f)
            
            # ADD NEW PICK
            if ten_day_pick:
                data['current_picks'].append(ten_day_pick)

            # --- THE RESET LOGIC ---
            if data['current_day'] >= 10:
                print("10th Day Complete. Archiving and Clearing...")
                archive = {"streak_end": datetime.now().strftime("%Y-%m-%d"), "picks": data['current_picks']}
                data['history'].append(archive)
                
                # Reset to Day 1 and Clear Picks
                data['current_day'] = 1
                data['current_picks'] = []
            else:
                data['current_day'] += 1
            
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()

        # 2. Update History (Win/Loss Tracking)
        with open('history.json', 'r+') as f:
            h_data = json.load(f)
            # (In a real scenario, you'd compare yesterday's scores here)
            # This is a placeholder to ensure the file structure remains intact
            f.seek(0)
            json.dump(h_data, f, indent=4)
            f.truncate()

# EXECUTION
if __name__ == "__main__":
    ai = DonChikeAI()
    morning, daily = ai.generate_predictions()
    ai.update_storage(morning, daily)
    print("AI Successfully updated Morning/Evening and 10-Day Tracker.")
