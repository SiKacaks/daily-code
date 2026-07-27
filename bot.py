import os
import requests
from playwright.sync_api import sync_playwright

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def scrape_live_codes():
    print("Launching browser to scrape deltaforcetools.gg...")
    try:
        with sync_playwright() as p:
            # Launch invisible Chromium browser
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Go to the website and wait for dynamic content to render
            page.goto("https://deltaforcetools.gg/", wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(3000) # Give extra 3 seconds for JS render

            # Extract all visible text from the webpage
            body_text = page.inner_text("body")
            browser.close()

            lines = [line.strip() for line in body_text.split("\n") if line.strip()]
            
            maps = ["Dam", "Layali Grove", "Brakkesh", "Space City", "Tide Prison", "AZ3"]
            scraped_results = []

            # Search extracted text line-by-line for Map names and matching 4-digit codes
            for i, line in enumerate(lines):
                for map_name in maps:
                    if map_name.lower() == line.lower() or map_name.lower() in line.lower():
                        # Look ahead in next lines for the 4-digit numeric code
                        for offset in range(1, 4):
                            if i + offset < len(lines):
                                potential_code = lines[i + offset]
                                if potential_code.isdigit() and len(potential_code) == 4:
                                    # Avoid adding duplicate map entries
                                    if not any(item['name'] == map_name for item in scraped_results):
                                        scraped_results.append({"name": map_name, "code": potential_code})
                                    break

            if scraped_results:
                print(f"Successfully scraped live codes: {scraped_results}")
                return scraped_results
            else:
                print("Failed to parse codes from page text.")
                return None

    except Exception as e:
        print(f"Scraping error: {e}")
        return None

def main():
    if not WEBHOOK_URL:
        print("CRITICAL ERROR: DISCORD_WEBHOOK_URL secret is missing!")
        exit(1)

    # 1. ALWAYS search and scrape the website first
    codes_data = scrape_live_codes()

    # 2. If scraping fails (website down/blocked), report error instead of fake data
    if not codes_data:
        print("Could not retrieve daily codes from website.")
        exit(1)

    # Build Discord Embed Message
    formatted_description = ""
    for item in codes_data:
        formatted_description += f"📍 **{item['name']}**\n# `{item['code']}`\n\n"

    embed = {
        "title": "🔑 Delta Force - Daily Door Codes",
        "url": "https://deltaforcetools.gg/",
        "color": 3066993,
        "description": formatted_description,
        "footer": {"text": "Live data scraped from deltaforcetools.gg"}
    }

    payload = {
        "username": "Delta Force Tools Bot",
        "embeds": [embed]
    }

    response = requests.post(WEBHOOK_URL, json=payload)
    if response.status_code in [200, 204]:
        print("SUCCESS: Live scraped codes posted to Discord!")
    else:
        print(f"FAILED: Status {response.status_code}: {response.text}")
        exit(1)

if __name__ == "__main__":
    main()
