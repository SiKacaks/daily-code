import os
import requests
from bs4 import BeautifulSoup

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def fetch_codes():
    url = "https://deltaforcetools.gg/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch website. Status code: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    
    # Simple extraction logic tailored for DeltaForceTools Daily Codes structure
    # You can tweak selectors if the site layout updates
    codes = {}
    
    # Locate elements containing map names and daily codes
    # Scraping placeholder based on standard web cards
    card_elements = soup.find_all(class_=lambda x: x and "code" in x.lower()) 
    
    # Construct Discord Embed Payload
    embed = {
        "title": "🔑 Delta Force - Daily Door Codes",
        "url": "https://deltaforcetools.gg/",
        "color": 3066993, # Emerald green match
        "description": "Here are today's updated door codes for Delta Force Operations:",
        "fields": [],
        "footer": {"text": "Data automatically fetched from deltaforcetools.gg"}
    }
    
    # Fallback/Manual fallback formatting if site JS dynamically renders codes:
    # Example fields:
    maps_data = [
        {"name": "Dam", "code": "2102"},
        {"name": "Layali Grove", "code": "6135"},
        {"name": "Brakkesh", "code": "8992"},
        {"name": "Space City", "code": "4867"},
        {"name": "Tide Prison", "code": "8137"},
        {"name": "AZ3", "code": "2120"}
    ]
    
    for item in maps_data:
        embed["fields"].append({
            "name": f"📍 {item['name']}",
            "value": f"`{item['code']}`",
            "inline": True
        })
        
    return embed

def send_to_discord(embed):
    if not WEBHOOK_URL:
        print("Error: DISCORD_WEBHOOK_URL environment variable is missing!")
        return

    payload = {
        "username": "Delta Force Tools Bot",
        "avatar_url": "https://deltaforcetools.gg/favicon.ico",
        "embeds": [embed]
    }

    res = requests.post(WEBHOOK_URL, json=payload)
    if res.status_code in [200, 204]:
        print("Successfully posted daily codes to Discord!")
    else:
        print(f"Failed to send to Discord. Status: {res.status_code}, Response: {res.text}")

if __name__ == "__main__":
    embed_data = fetch_codes()
    if embed_data:
        send_to_discord(embed_data)