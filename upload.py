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
            # Step 1: Navigate to the first page
            print(f"STEP 1: Navigating to initial page: {page_url}")
            page.goto(page_url, wait_until="domcontentloaded", timeout=90000)

            # Step 2: Click the "Download Now" button
            print("STEP 2: Looking for the first 'Download' button...")
            first_download_button = page.get_by_role("link", name=re.compile("download", re.IGNORECASE)).first
            first_download_button.wait_for(timeout=30000)
            print("Found first 'Download' button. Clicking it...")
            first_download_button.click()

            # Step 3: Click the "High Quality" button
            print("STEP 3: Waiting for 'High Quality' button to appear after timer...")
            high_quality_button = page.locator('a:has-text("High Quality")')
            high_quality_button.wait_for(state="visible", timeout=20000)
            print("Found 'High Quality' button. Clicking it to go to the next page...")
            high_quality_button.click()
            
            # Step 4: Arrive on the final download page
            print("STEP 4: Waiting for the final download page to load...")
            page.wait_for_load_state("domcontentloaded", timeout=60000)
            print(f"Landed on final page: {page.url}")

            # --- THE FINAL FIX ---
            # The URL is already on the page. We just need to find the link
            # and read its 'href' attribute. No click is needed.
            print("STEP 5: Locating the final download link on the page...")
            final_link_locator = page.locator("a:has-text('Download file')")

            # Wait for the link to be present
            final_link_locator.wait_for(timeout=15000)
            
            # Read the URL directly from the link's href attribute
            final_link = final_link_locator.get_attribute("href")
            # --- END OF FIX ---

            if final_link:
                 print(f"SUCCESS: Captured final direct link: {final_link}")
            else:
                print("ERROR: Found the link, but it had no href attribute.")

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
        # Get only the first URL from the file for the test
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
