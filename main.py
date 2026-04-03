import os
import json
import requests
from datetime import datetime

class DonChikeAI:
    def __init__(self):
        # This pulls the key you set in GitHub Secrets
        self.api_key = os.getenv('FOOTBALL_API_KEY')
        self.headers = {
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': 'v3.football.api-sports.io'
        }

    def run(self):
        print(f"--- AI STARTING: {datetime.now()} ---")
        
        # Test connection to EPL (League 39)
        url = "https://v3.football.api-sports.io/fixtures?league=39&season=2025&next=10"
        
        try:
            response = requests.get(url, headers=self.headers)
            print(f"API Response Status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"ERROR: API returned {response.status_code}. Check subscription!")
                return

            data = response.json().get('response', [])
            print(f"Games Found: {len(data)}")

            if not data:
                print("No games found. Trying backup league (La Liga)...")
                # Try League 140 if EPL is empty
                url = "https://v3.football.api-sports.io/fixtures?league=140&season=2025&next=10"
                data = requests.get(url, headers=self.headers).json().get('response', [])

            # Build the ticket
            m_ticket = []
            for i, f in enumerate(data[:10]):
                m_ticket.append({
                    "day": f"Day {i+1}",
                    "date": f['fixture']['date'][5:10], # MM-DD
                    "match": f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}"
                })

            # Save to tracker.json
            with open('tracker.json', 'w') as f:
                json.dump({"master_ticket": m_ticket}, f, indent=4)
            print("Successfully updated tracker.json with real games.")

        except Exception as e:
            print(f"CRITICAL ERROR: {str(e)}")

if __name__ == "__main__":
    DonChikeAI().run()
