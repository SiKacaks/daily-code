import os
import requests
from playwright.sync_api import sync_playwright

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def scrape_official_daily_passwords():
    print("Launching browser to scrape playdeltaforce.com...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox"]
            )
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            # Go directly to the official HQ page
            page.goto("https://www.playdeltaforce.com/events/hq/en/", wait_until="networkidle", timeout=45000)
            page.wait_for_timeout(5000)  # Wait 5 seconds for dynamic JS rendering

            # Read all body text
            body_text = page.inner_text("body")
            browser.close()

            lines = [line.strip() for line in body_text.split("\n") if line.strip()]
            
            maps = ["Zero Dam", "Layali Grove", "Brakkesh", "Space City", "Tide Prison", "AZ3"]
            scraped_results = []

            # Search text line-by-line for Map names and corresponding 4-digit passwords
            for i, line in enumerate(lines):
                for map_name in maps:
                    if map_name.lower() in line.lower():
                        # Search nearby lines for the 4-digit code
                        for offset in range(1, 5):
                            if i + offset < len(lines):
                                potential_code = lines[i + offset]
                                if potential_code.isdigit() and len(potential_code) == 4:
                                    if not any(item['name'] == map_name for item in scraped_results):
                                        scraped_results.append({"name": map_name, "code": potential_code})
                                    break

            if scraped_results:
                print(f"SUCCESSFULLY SCRAPED OFFICIAL PASSWORDS: {scraped_results}")
                return scraped_results
            else:
                print("Could not locate passwords in extracted text.")
                return None

    except Exception as e:
        print(f"Scraping official site failed: {e}")
        return None

def main():
    if not WEBHOOK_URL:
        print("CRITICAL ERROR: DISCORD_WEBHOOK_URL secret is missing!")
        exit(1)

    # Scrape from official site
    codes_data = scrape_official_daily_passwords()

    if not codes_data:
        print("Scraper failed to pull daily passwords from official site!")
        exit(1)

    # Format into large text headers
    formatted_description = ""
    for item in codes_data:
        formatted_description += f"📍 **{item['name']}**\n# `{item['code']}`\n\n"

    embed = {
        "title": "🔑 Delta Force - Daily Passwords",
        "url": "https://www.playdeltaforce.com/events/hq/en/",
        "color": 3066993,
        "description": formatted_description,
        "footer": {"text": "Official data scraped directly from playdeltaforce.com"}
    }

    payload = {
        "username": "Daily Code Doors Bot",
        "embeds": [embed]
    }

    response = requests.post(WEBHOOK_URL, json=payload)
    if response.status_code in [200, 204]:
        print("SUCCESS: Official passwords posted to Discord!")
    else:
        print(f"FAILED: Status {response.status_code}: {response.text}")
        exit(1)

if __name__ == "__main__":
    main()
