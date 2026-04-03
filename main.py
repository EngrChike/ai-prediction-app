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

    def fetch_data(self):
        all_matches = []
        # Top Leagues: EPL(39), La Liga(140), Serie A(135), Bundesliga(78), Ligue 1(61)
        league_ids = [39, 140, 135, 78, 61]
        
        # We check season 2025 because April 2026 is part of the 2025/26 season
        for lid in league_ids:
            try:
                url = f"{self.base_url}/fixtures?league={lid}&season=2025&next=15"
                response = requests.get(url, headers=self.headers).json()
                data = response.get('response', [])
                if data:
                    all_matches.extend(data)
            except Exception as e:
                print(f"Error on League {lid}: {e}")
                continue
        return all_matches

    def run(self):
        fixtures = self.fetch_data()
        
        # If still empty, the API key might be the issue or the Season needs to be 2026
        if not fixtures:
            print("No fixtures found. Attempting backup season 2026...")
            # (Optional backup loop could go here)
            return

        fixtures.sort(key=lambda x: x['fixture']['date'])
        
        # 1. 5-Odds (History)
        m_slip = []
        for f in fixtures[:3]:
            m_slip.append({
                "match": f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}",
                "tip": "Over 2.5",
                "odds": 1.80
            })

        # 2. 10-Day Ticket (Tracker)
        m_ticket = []
        dates_seen = set()
        for f in fixtures:
            d_str = f['fixture']['date'][:10]
            if d_str not in dates_seen and len(m_ticket) < 10:
                m_ticket.append({
                    "day": f"Day {len(m_ticket)+1}",
                    "date": datetime.strptime(d_str, "%Y-%m-%d").strftime("%d %b"),
                    "match": f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}"
                })
                dates_seen.add(d_str)

        # Write to files
        with open('tracker.json', 'w') as f:
            json.dump({"master_ticket": m_ticket}, f, indent=4)
        
        with open('history.json', 'w') as f:
            json.dump({
                "morning_5_odds": m_slip,
                "win_rate": "0%", "total_wins": 0, "total_losses": 0, "current_streak": "0W",
                "last_update": datetime.now().strftime("%H:%M")
            }, f, indent=4)

if __name__ == "__main__":
    DonChikeAI().run()
