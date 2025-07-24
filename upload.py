import os
import re 
import time
from playwright.sync_api import sync_playwright
from urllib.parse import urljoin

# --- THIS IS A DEBUGGING SCRIPT ---
# The goal is to take a picture of the final page.

def capture_final_page_state(page_url: str):
    """Navigates to the final page and saves a screenshot and the HTML code for analysis."""
    
    base_url = "https://vide0.net"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            print("DEBUG: STEP 1 - Navigating to initial page...")
            page.goto(page_url, wait_until="domcontentloaded", timeout=90000)

            print("DEBUG: STEP 2 - Clicking the first 'Download' button...")
            first_download_button = page.get_by_role("link", name=re.compile("download", re.IGNORECASE)).first
            first_download_button.wait_for(timeout=30000)
            first_download_button.click()

            print("DEBUG: STEP 3 - Getting the URL from 'High Quality' button...")
            high_quality_button = page.locator('a:has-text("High Quality")')
            high_quality_button.wait_for(state="visible", timeout=20000)
            
            relative_url = high_quality_button.get_attribute("href")
            full_destination_url = urljoin(base_url, relative_url)
            print(f"DEBUG: Constructed full URL: {full_destination_url}")
            
            print("DEBUG: STEP 4 - Navigating to the final page...")
            page.goto(full_destination_url, wait_until="domcontentloaded", referer=page.url)
            print(f"DEBUG: Successfully landed on final page: {page.url}")

            # --- THE MOST IMPORTANT PART: THE SNAPSHOT ---
            print("DEBUG: STEP 5 - The page has loaded. Waiting 5 seconds for any background scripts to finish...")
            time.sleep(5) # This is crucial. We give the page's scripts time to add the final link.

            print("DEBUG: Taking screenshot and saving HTML content...")
            
            # Save a picture of what the robot sees
            page.screenshot(path="debug_screenshot.png", full_page=True)
            print(">> Successfully saved screenshot to debug_screenshot.png")

            # Save the raw HTML code that the robot sees
            with open("debug_page_content.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            print(">> Successfully saved page HTML to debug_page_content.html")
            
        except Exception as e:
            print(f"AN ERROR OCCURRED DURING DEBUGGING: {e}")
            # Still try to save artifacts even on error
            page.screenshot(path="debug_screenshot.png", full_page=True)
            with open("debug_page_content.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            print(">> Saved error state screenshot and HTML.")
        finally:
            print("DEBUG: Script finished. Closing browser.")
            browser.close()

def main():
    URL_FILE = "urls.txt"
    print("--- Running DoodStream DEBUGGING Script ---")
    with open(URL_FILE, 'r') as f:
        url_to_process = f.readline().strip()

    if url_to_process:
        capture_final_page_state(url_to_process)

if __name__ == "__main__":
    main()
