import os
import json
import requests
from datetime import datetime

class DonChikeAI:
    def __init__(self):
        self.api_key = os.getenv('FOOTBALL_API_KEY')
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = {
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': 'v3.football.api-sports.io'
        }

    def fetch_all_upcoming(self):
        """Fetches from top 5 European leagues to guarantee 10 games."""
        all_fixtures = []
        leagues = [39, 140, 135, 78, 61] # EPL, La Liga, Serie A, Bundesliga, Ligue 1
        current_year = datetime.now().year
        
        for league_id in leagues:
            try:
                # APIs usually use the start year of the season (2025 for 2025/26)
                url = f"{self.base_url}/fixtures?league={league_id}&season=2025&next=15"
                response = requests.get(url, headers=self.headers)
                res_data = response.json().get('response', [])
                if res_data:
                    all_fixtures.extend(res_data)
            except Exception as e:
                print(f"Error fetching league {league_id}: {e}")
                continue
        
        return all_fixtures

    def run_engine(self):
        fixtures = self.fetch_all_upcoming()
        # Sort by date so Day 1 is the earliest
        fixtures.sort(key=lambda x: x['fixture']['date'])

        # 1. Generate 5-Odds (Morning Slip)
        morning_slip = []
        for f in fixtures[:3]:
            morning_slip.append({
                "match": f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}",
                "tip": "Over 2.5 / GG",
                "odds": 1.85
            })

        # 2. Generate 10-Day Master Ticket (1 unique game per day)
        master_ticket = []
        seen_dates = set()
        for f in fixtures:
            date_str = f['fixture']['date'][:10] # YYYY-MM-DD
            if date_str not in seen_dates and len(master_ticket) < 10:
                master_ticket.append({
                    "day": f"Day {len(master_ticket) + 1}",
                    "date": datetime.strptime(date_str, "%Y-%m-%d").strftime("%b %d"),
                    "match": f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}",
                    "tip": "Over 2.5"
                })
                seen_dates.add(date_str)

        return morning_slip, master_ticket

    def save_data(self, morning, master):
        # Update tracker.json
        with open('tracker.json', 'w') as f:
            json.dump({
                "master_ticket": master, 
                "updated_at": datetime.now().strftime("%Y-%m-%d")
            }, f, indent=4)

        # Update history.json
        try:
            with open('history.json', 'r') as f:
                h_data = json.load(f)
        except:
            h_data = {"total_wins": 0, "total_losses": 0, "win_rate": "0%", "current_streak": "0W"}

        h_data['morning_5_odds'] = morning
        h_data['last_update'] = datetime.now().strftime("%H:%M")
        
        with open('history.json', 'w') as f:
            json.dump(h_data, f, indent=4)

if __name__ == "__main__":
    bot = DonChikeAI()
    m, t = bot.run_engine()
    bot.save_data(m, t)
    print("AI MASTER: Data Sync Complete.")
