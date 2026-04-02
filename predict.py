import requests
import json
import math
from datetime import datetime

class DonChikeAI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {'x-rapidapi-key': api_key, 'x-rapidapi-host': 'v3.football.api-sports.io'}
        self.base_url = "https://v3.football.api-sports.io"

    def get_match_data(self, fixture_id):
        # 1. Check High Intensity & Stats
        stats_res = requests.get(f"{self.base_url}/fixtures/statistics?fixture={fixture_id}", headers=self.headers).json()
        
        # 2. Check Lineups & Injuries
        lineup_res = requests.get(f"{self.base_url}/fixtures/lineups?fixture={fixture_id}", headers=self.headers).json()
        
        # 3. Head to Head
        # (Logic: Compare last 5 meetings)
        
        return stats_res, lineup_res

    def calculate_5_odds(self, fixtures):
        """Logic to select specific markets: GG, Over, Corners, or Win"""
        selected_picks = []
        total_odds = 1.0
        
        for f in fixtures:
            # logic: If Team A shots on target > 6 and Team B shots on target > 5 -> Predict GG (Both Teams to Score)
            # logic: If Top Scorer is present and defense injury > 2 -> Predict Over 2.5
            if total_odds < 5.0:
                # Add pick to slip
                pass 
        return selected_picks

    def manage_10_day_streak(self, daily_pick_result):
        """Handles the '10th day finish and clear' rule"""
        with open('tracker.json', 'r+') as f:
            data = json.load(f)
            if daily_pick_result == "WIN":
                data['current_day'] += 1
            else:
                data['current_day'] = 1 # Reset on loss
            
            if data['current_day'] > 10:
                data['history'].append(data['current_picks'])
                data['current_day'] = 1 # Clear and Restart
                data['current_picks'] = []
            
            f.seek(0)
            json.dump(data, f, indent=4)
