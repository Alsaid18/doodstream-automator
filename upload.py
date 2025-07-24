import os
import re 
import requests
import time
from playwright.sync_api import sync_playwright

def get_final_mp4_link(page_url: str):
    """
    Automates the full multi-step process to get the final MP4 download link,
    bypassing anti-bot checks by navigating directly.
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

            # --- THE DEFINITIVE FIX ---
            # Step 3a: Don't click the next button blindly. First, read its destination.
            print("STEP 3: Locating the 'High Quality' button and reading its destination URL...")
            high_quality_button = page.locator('a:has-text("High Quality")')
            high_quality_button.wait_for(state="visible", timeout=20000)
            
            # Read the URL from the button's href attribute
            destination_url = high_quality_button.get_attribute("href")
            print(f"Successfully read destination URL: {destination_url}")
            
            # Step 3b: Navigate to that destination URL directly, passing the current page as the "Referer".
            # This makes the request look like a legitimate click to the server.
            print("Navigating directly to the destination URL to bypass security check...")
            current_page_url = page.url
            page.goto(destination_url, wait_until="domcontentloaded", referer=current_page_url)
            # --- END OF FIX ---
            
            print(f"STEP 4: Successfully landed on final page: {page.url}")

            # Step 5: Find the final link on this new page by its destination
            print("STEP 5: Locating the final link by its 'cloudatacdn.com' destination...")
            final_link_locator = page.locator('a[href*="cloudatacdn.com"]')
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
