import os
import json
import requests
from datetime import datetime

class DonChikeDeepAI:
    def __init__(self):
        self.api_key = os.getenv('FOOTBALL_API_KEY')
        self.headers = {
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': 'v3.football.api-sports.io'
        }

    def get_analysis(self, home_id, away_id):
        """Checks H2H and Form to calculate Intensity."""
        try:
            # 1. Fetch Head-to-Head
            url = f"https://v3.football.api-sports.io/fixtures/headtohead?h2h={home_id}-{away_id}"
            h2h_data = requests.get(url, headers=self.headers).json().get('response', [])
            
            # 2. Check intensity (e.g., have 80% of their last games been Over 2.5?)
            over_25_count = sum(1 for g in h2h_data[:5] if (g['goals']['home'] + g['goals']['away']) > 2.5)
            
            # 3. Decision Logic
            if over_25_count >= 3: # If 3 out of last 5 were high intensity
                return True, over_25_count * 20 # Return True + Intensity Score
            return False, 0
        except:
            return False, 0

    def run(self):
        # Scan EPL and Champions League for the best matches
        leagues = [39, 2] 
        final_picks = []
        
        for lid in leagues:
            url = f"https://v3.football.api-sports.io/fixtures?league={lid}&season=2025&next=10"
            fixtures = requests.get(url, headers=self.headers).json().get('response', [])
            
            for f in fixtures:
                home_id = f['teams']['home']['id']
                away_id = f['teams']['away']['id']
                
                # RUN THE BRAIN: Analyze H2H and Intensity
                is_good, intensity_score = self.get_analysis(home_id, away_id)
                
                if is_good and len(final_picks) < 10:
                    final_picks.append({
                        "day": f"Day {len(final_picks)+1}",
                        "date": datetime.strptime(f['fixture']['date'][:10], "%Y-%m-%d").strftime("%d %b"),
                        "match": f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}",
                        "intensity": f"{intensity_score}%",
                        "analysis": "High H2H Over 2.5 Trend"
                    })

        # Save the analyzed data
        with open('tracker.json', 'w') as f:
            json.dump({"master_ticket": final_picks}, f, indent=4)
        print(f"Deep Analysis Complete: {len(final_picks)} high-intensity games locked.")

if __name__ == "__main__":
    DonChikeDeepAI().run()
