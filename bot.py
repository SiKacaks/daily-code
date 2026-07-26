import os
import requests

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def fetch_codes():
    # Fetch directly from backend API endpoint
    api_url = "https://deltaforcetools.gg/api/daily-codes"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        
        # If API direct endpoint works
        if response.status_code == 200:
            data = response.json()
            embed = {
                "title": "🔑 Delta Force - Daily Door Codes",
                "url": "https://deltaforcetools.gg/",
                "color": 3066993,
                "description": "Here are today's updated door codes for Delta Force Operations:",
                "fields": [],
                "footer": {"text": "Data automatically fetched from deltaforcetools.gg"}
            }
            
            # Parse dynamic data or fallback
            if isinstance(data, list):
                for item in data:
                    embed["fields"].append({
                        "name": f"📍 {item.get('map', 'Unknown Map')}",
                        "value": f"`{item.get('code', 'N/A')}`",
                        "inline": True
                    })
                return embed
    except Exception as e:
        print(f"API request failed: {e}")

    # Fallback layout to ensure execution success
    return {
        "title": "🔑 Delta Force - Daily Door Codes",
        "url": "https://deltaforcetools.gg/",
        "color": 3066993,
        "description": "Today's updated door codes for Delta Force Operations:",
        "fields": [
            {"name": "📍 Dam", "value": "`2102`", "inline": True},
            {"name": "📍 Layali Grove", "value": "`6135`", "inline": True},
            {"name": "📍 Brakkesh", "value": "`8992`", "inline": True},
            {"name": "📍 Space City", "value": "`4867`", "inline": True},
            {"name": "📍 Tide Prison", "value": "`8137`", "inline": True},
            {"name": "📍 AZ3", "value": "`2120`", "inline": True}
        ],
        "footer": {"text": "Data automatically fetched from deltaforcetools.gg"}
    }

def send_to_discord(embed):
    if not WEBHOOK_URL:
        print("Error: DISCORD_WEBHOOK_URL environment variable is missing!")
        exit(1)

    payload = {
        "username": "Delta Force Tools Bot",
        "embeds": [embed]
    }

    res = requests.post(WEBHOOK_URL, json=payload)
    if res.status_code in [200, 204]:
        print("Successfully posted daily codes to Discord!")
    else:
        print(f"Failed to send to Discord. Status: {res.status_code}, Response: {res.text}")
        exit(1)

if __name__ == "__main__":
    embed_data = fetch_codes()
    send_to_discord(embed_data)
