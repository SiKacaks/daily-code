import os
import requests
from playwright.sync_api import sync_playwright

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def scrape_live_codes():
    print("Launching Chromium browser to scrape live codes...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox"]
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            # Go to website
            page.goto("https://deltaforcetools.gg/", wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(5000)  # Wait 5 seconds for JS daily codes to render

            body_text = page.inner_text("body")
            browser.close()

            lines = [line.strip() for line in body_text.split("\n") if line.strip()]
            
            maps = ["Dam", "Layali Grove", "Brakkesh", "Space City", "Tide Prison", "AZ3"]
            scraped_results = []

            for i, line in enumerate(lines):
                for map_name in maps:
                    if map_name.lower() in line.lower():
                        # Search adjacent lines for 4-digit daily code
                        for offset in range(1, 4):
                            if i + offset < len(lines):
                                val = lines[i + offset]
                                if val.isdigit() and len(val) == 4:
                                    if not any(item['name'] == map_name for item in scraped_results):
                                        scraped_results.append({"name": map_name, "code": val})
                                    break

            if scraped_results:
                print(f"SCRAPE SUCCESSFUL: {scraped_results}")
                return scraped_results
            else:
                print("Could not parse 4-digit codes from page text.")
                return None

    except Exception as e:
        print(f"Scraping failed with error: {e}")
        return None

def main():
    if not WEBHOOK_URL:
        print("CRITICAL ERROR: DISCORD_WEBHOOK_URL secret is missing!")
        exit(1)

    # 1. Scrape live data dynamically
    codes_data = scrape_live_codes()

    if not codes_data:
        print("Scraper failed to pull live codes!")
        exit(1)

    # 2. Build Discord Message with Header formatting
    formatted_description = ""
    for item in codes_data:
        formatted_description += f"📍 **{item['name']}**\n# `{item['code']}`\n\n"

    embed = {
        "title": "🔑 Delta Force - Daily Door Codes",
        "url": "https://deltaforcetools.gg/",
        "color": 3066993,
        "description": formatted_description,
        "footer": {"text": "Live data scraped directly from deltaforcetools.gg"}
    }

    payload = {
        "username": "Delta Force Tools Bot",
        "embeds": [embed]
    }

    response = requests.post(WEBHOOK_URL, json=payload)
    if response.status_code in [200, 204]:
        print("SUCCESS: Live codes posted to Discord!")
    else:
        print(f"FAILED: Status {response.status_code}: {response.text}")
        exit(1)

if __name__ == "__main__":
    main()
