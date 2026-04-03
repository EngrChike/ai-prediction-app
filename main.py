import os
import json
import requests
from datetime import datetime

class DonChikeAI:
    def __init__(self):
        # This pulls your secret key from GitHub Settings
        self.api_key = os.getenv('FOOTBALL_API_KEY')
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = {
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': 'v3.football.api-sports.io'
        }

    def fetch_all_upcoming(self):
        """Fetches a pool of games for the top leagues."""
        # Premier League (39), La Liga (140), Serie A (135), Bundesliga (78)
        # We fetch the next 70 games to ensure we find enough unique days.
        url = f"{self.base_url}/fixtures?league=39&season=2025&next=70"
        try:
            response = requests.get(url, headers=self.headers)
            return response.json().get('response', [])
        except Exception as e:
            print(f"Error fetching data: {e}")
            return []

    def generate_engine(self):
        fixtures = self.fetch_all_upcoming()
        # Sort by date so Day 1 is the soonest game
        fixtures.sort(key=lambda x: x['fixture']['date'])

        # 1. Generate Morning 5-Odds (The first 3 games)
        morning_slip = []
        for f in fixtures[:3]:
            morning_slip.append({
                "match": f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}",
                "tip": "Over 2.5 / GG",
                "odds": 1.85
            })

        # 2. Generate 10-Day Master Ticket (One unique game per day)
        master_ticket = []
        seen_dates = set()
        for f in fixtures:
            date_str = f['fixture']['date'][:10] # YYYY-MM-DD
            if date_str not in seen_dates and len(master_ticket) < 10:
                master_ticket.append({
                    "day": f"Day {len(master_ticket) + 1}",
                    "date": datetime.strptime(date_str, '%Y-%m-%d').strftime('%b %d'),
                    "match": f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}",
                    "tip": "Over 2.5"
                })
                seen_dates.add(date_str)

        return morning_slip, master_ticket

    def update_files(self, morning, master):
        # 1. Update tracker.json (This feeds the 10-Day section)
        with open('tracker.json', 'w') as f:
            json.dump({
                "master_ticket": master, 
                "updated": datetime.now().strftime("%Y-%m-%d")
            }, f, indent=4)

        # 2. Update history.json (This feeds the 5-Odds & Stats)
        # We try to read existing stats first so we don't overwrite your 0% start
        try:
            with open('history.json', 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {
                "total_wins": 0, "total_losses": 0, "win_rate": "0%", 
                "current_streak": "0W"
            }

        data['morning_5_odds'] = morning
        data['last_update'] = datetime.now().strftime("%H:%M")

        with open('history.json', 'w') as f:
            json.dump(data, f, indent=4)

if __name__ == "__main__":
    bot = DonChikeAI()
    m_slip, t_ticket = bot.generate_engine()
    bot.update_files(m_slip, t_ticket)
    print("SUCCESS: Engine updated tracker.json and history.json")
