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
        """Fetches a large pool of games to find 10 unique days."""
        # Leagues: 39 (EPL), 140 (La Liga), 135 (Serie A), 78 (Bundesliga)
        url = f"{self.base_url}/fixtures?league=39&season=2026&next=70"
        response = requests.get(url, headers=self.headers)
        return response.json().get('response', [])

    def generate_engine(self):
        fixtures = self.fetch_all_upcoming()
        fixtures.sort(key=lambda x: x['fixture']['date'])

        # 1. Generate 5-Odds (Morning/Evening)
        # Using the first 3 high-intensity games for the 5-odds slip
        morning_slip = []
        for f in fixtures[:3]:
            morning_slip.append({
                "match": f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}",
                "tip": "Over 2.5 / GG",
                "odds": 1.80
            })

        # 2. Generate 10-Day Master Accumulator (One per day)
        master_ticket = []
        seen_dates = set()
        for f in fixtures:
            date_str = f['fixture']['date'][:10]
            if date_str not in seen_dates and len(master_ticket) < 10:
                master_ticket.append({
                    "day": f"Day {len(master_ticket) + 1}",
                    "date": date_str,
                    "match": f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}",
                    "tip": "Over 2.5"
                })
                seen_dates.add(date_str)

        return morning_slip, master_ticket

    def update_files(self, morning, master):
        # Update tracker.json (The 10-Day Ticket)
        with open('tracker.json', 'w') as f:
            json.dump({"master_ticket": master, "updated": datetime.now().strftime("%Y-%m-%d")}, f, indent=4)

        # Update history.json (The 5-Odds & Stats)
        with open('history.json', 'r+') as f:
            data = json.load(f)
            data['morning_5_odds'] = morning
            data['last_update'] = datetime.now().strftime("%H:%M")
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()

if __name__ == "__main__":
    bot = DonChikeAI()
    m_slip, t_ticket = bot.generate_engine()
    bot.update_files(m_slip, t_ticket)
    print("AI Engine: Morning Slip and 10-Day Ticket Updated.")
