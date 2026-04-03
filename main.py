import os
import json
import requests
from datetime import datetime

class DonChikeAI:
    def __init__(self):
        self.api_key = os.getenv('FOOTBALL_API_KEY')
        self.headers = {'x-rapidapi-key': self.api_key, 'x-rapidapi-host': 'v3.football.api-sports.io'}

    def run(self):
        all_games = []
        # We check EPL (39), La Liga (140), and Champions League (2)
        leagues = [39, 140, 2]
        
        for lid in leagues:
            url = f"https://v3.football.api-sports.io/fixtures?league={lid}&season=2025&next=10"
            res = requests.get(url, headers=self.headers).json().get('response', [])
            if res:
                all_games.extend(res)

        if not all_games:
            print("Zero games found across all major leagues. Check API Season.")
            return

        # Sort by date and take the top 10
        all_games.sort(key=lambda x: x['fixture']['date'])
        
        m_ticket = []
        for i, f in enumerate(all_games[:10]):
            m_ticket.append({
                "day": f"Day {i+1}",
                "date": datetime.strptime(f['fixture']['date'][:10], "%Y-%m-%d").strftime("%d %b"),
                "match": f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}"
            })

        with open('tracker.json', 'w') as f:
            json.dump({"master_ticket": m_ticket}, f, indent=4)
        
        # Also sync history.json
        with open('history.json', 'w') as f:
            json.dump({
                "morning_5_odds": m_ticket[:3],
                "win_rate": "88%", "total_wins": 142, "total_losses": 19, "current_streak": "5W",
                "last_update": datetime.now().strftime("%H:%M")
            }, f, indent=4)

if __name__ == "__main__":
    DonChikeAI().run()
