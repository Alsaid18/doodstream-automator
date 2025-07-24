import os
import re 
import requests
import time
from playwright.sync_api import sync_playwright

def get_final_mp4_link(page_url: str):
    """
    Automates the full multi-step process to get the final MP4 download link.
    """
    final_link = None
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            # Steps 1-4 are working perfectly.
            print(f"STEP 1: Navigating to initial page: {page_url}")
            page.goto(page_url, wait_until="domcontentloaded", timeout=90000)

            print("STEP 2: Looking for the first 'Download' button...")
            first_download_button = page.get_by_role("link", name=re.compile("download", re.IGNORECASE)).first
            first_download_button.wait_for(timeout=30000)
            print("Found first 'Download' button. Clicking it...")
            first_download_button.click()

            print("STEP 3: Waiting for 'High Quality' button to appear after timer...")
            high_quality_button = page.locator('a:has-text("High Quality")')
            high_quality_button.wait_for(state="visible", timeout=20000)
            print("Found 'High Quality' button. Clicking it to go to the next page...")
            high_quality_button.click()
            
            print("STEP 4: Waiting for the final download page to load...")
            page.wait_for_load_state("domcontentloaded", timeout=60000)
            print(f"Landed on final page: {page.url}")

            # --- THE DEFINITIVE FIX ---
            # Find the link by its destination URL, not by its text.
            # This looks for any <a> tag where the href attribute contains "cloudatacdn.com".
            print("STEP 5: Locating the link by its href destination 'cloudatacdn.com'...")
            final_link_locator = page.locator('a[href*="cloudatacdn.com"]')
            # --- END OF FIX ---
            
            final_link_locator.wait_for(timeout=15000)
            final_link = final_link_locator.get_attribute("href")

            if final_link:
                 print(f"SUCCESS: Captured final direct link: {final_link}")
            else:
                print("ERROR: Found the link, but could not read its href attribute.")

        except Exception as e:
            print(f"AN ERROR OCCURRED: {e}")
        finally:
            print("Closing browser.")
            browser.close()
            
        return final_link

def main():
    URL_FILE = "urls.txt"
    print("--- Starting DoodStream Link Capture Script ---")
    
    with open(URL_FILE, 'r') as f:
        url_to_process = f.readline().strip()

    if url_to_process:
        print(f"--- Processing URL: {url_to_process} ---")
        direct_video_link = get_final_mp4_link(url_to_process)
        
        if direct_video_link:
            print("\n--- FINAL RESULT ---")
            print("The script successfully found the following direct download URL:")
            print(direct_video_link)
            print("--------------------\n")
        else:
            print("\n--- FINAL RESULT ---")
            print("The script failed to retrieve the direct download URL.")
            print("--------------------\n")
    else:
        print("No URLs found in urls.txt")

if __name__ == "__main__":
    main()
