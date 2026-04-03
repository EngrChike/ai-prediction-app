import os
import json
import requests
from datetime import datetime

class DonChikeAI:
    def __init__(self):
        self.api_key = os.getenv('FOOTBALL_API_KEY')
        self.headers = {
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': 'v3.football.api-sports.io'
        }

    def run(self):
        # We use Season 2025 because April 2026 is the tail end of the 2025/26 season
        url = "https://v3.football.api-sports.io/fixtures?league=39&season=2025&next=15"
        
        try:
            response = requests.get(url, headers=self.headers)
            data = response.json().get('response', [])
            
            # If EPL (39) is empty, try La Liga (140) as a backup
            if not data:
                url = "https://v3.football.api-sports.io/fixtures?league=140&season=2025&next=15"
                data = requests.get(url, headers=self.headers).json().get('response', [])

            m_ticket = []
            for i, f in enumerate(data[:10]):
                # Formatting match info
                home = f['teams']['home']['name']
                away = f['teams']['away']['name']
                date_raw = f['fixture']['date'] # e.g. 2026-04-05T15:00:00+00:00
                
                m_ticket.append({
                    "day": f"Day {i+1}",
                    "date": datetime.strptime(date_raw[:10], "%Y-%m-%d").strftime("%d %b"),
                    "match": f"{home} vs {away}"
                })

            # SAVE DATA
            with open('tracker.json', 'w') as f:
                json.dump({"master_ticket": m_ticket}, f, indent=4)
            
            # Update history with 0 stats for the fresh start
            with open('history.json', 'w') as f:
                json.dump({
                    "morning_5_odds": m_ticket[:3], # Using first 3 for morning
                    "win_rate": "0%", "total_wins": 0, "total_losses": 0, "current_streak": "0W",
                    "last_update": datetime.now().strftime("%H:%M")
                }, f, indent=4)
                
            print(f"Successfully synced {len(m_ticket)} games!")

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    DonChikeAI().run()
