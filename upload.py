import os
import re 
import requests
import time
from playwright.sync_api import sync_playwright

# --- Configuration ---
API_KEY = os.getenv("DOODSTREAM_API_KEY") 
URL_FILE = "urls.txt"
UPLOAD_API_URL = f"https://doodapi.co/api/upload/url?key={API_KEY}&url="

def get_final_mp4_link(page_url: str):
    """
    Automates the full multi-step process to get the final MP4 download link.
    """
    final_link = None
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            print(f"STEP 1: Navigating to initial page: {page_url}")
            page.goto(page_url, wait_until="domcontentloaded", timeout=90000)

            print("STEP 2: Looking for the first 'Download' button by its text...")
            first_download_button = page.get_by_role("link", name=re.compile("download", re.IGNORECASE)).first
            first_download_button.wait_for(timeout=30000)
            print("Found first 'Download' button. Clicking it...")
            first_download_button.click()

            print("STEP 3: Waiting for 'High Quality' button to appear after timer...")
            high_quality_button = page.locator('a:has-text("High Quality")')
            high_quality_button.wait_for(state="visible", timeout=20000)
            print("Found 'High Quality' button. Clicking it to go to the next page...")
            high_quality_button.click()
            
            print("STEP 4: Waiting for the download page to load...")
            page.wait_for_load_state("domcontentloaded", timeout=60000)
            print(f"Landed on page: {page.url}")

            print("STEP 5: Preparing to capture the final MP4 link...")
            
            with page.expect_download(timeout=30000) as download_info:
                # --- THIS IS THE FIX ---
                # Find the final button by its visible text "Download File"
                print("Clicking the final 'Download File' button...")
                final_download_button = page.get_by_role("link", name=re.compile("Download File", re.IGNORECASE)).first
                # --- END OF FIX ---
                
                final_download_button.wait_for(timeout=15000)
                final_download_button.click()
            
            download = download_info.value
            final_link = download.url
            download.cancel()

            print(f"SUCCESS: Captured final MP4 link: {final_link}")

        except Exception as e:
            print(f"AN ERROR OCCURRED: {e}")
        finally:
            print("Closing browser.")
            browser.close()
            
        return final_link

def upload_to_doodstream(direct_url: str):
    """Sends the direct link to the DoodStream API to start the upload."""
    if not direct_url:
        print("No direct URL provided, skipping upload.")
        return

    print(f"Requesting remote upload for: {direct_url}")
    try:
        response = requests.get(UPLOAD_API_URL + direct_url, timeout=60)
        api_response_json = response.json()
        print("API Response:", api_response_json)

        if response.status_code == 200 and api_response_json.get('status') == 200:
             print("API call successful. DoodStream is now processing the video.")
        else:
            print(f"Error reported by DoodStream API. Status: {response.status_code}, Msg: {api_response_json.get('msg')}")

    except Exception as e:
        print(f"An error occurred during API call: {e}")

def main():
    if not API_KEY:
        print("CRITICAL ERROR: DOODSTREAM_API_KEY secret is not set in GitHub repository settings.")
        return
        
    print("Starting DoodStream automation process...")
    with open(URL_FILE, 'r') as f:
        urls_to_process = [line.strip() for line in f if line.strip()]

    for url in urls_to_process:
        print(f"\n--- Processing URL: {url} ---")
        direct_video_link = get_final_mp4_link(url)
        if direct_video_link:
            upload_to_doodstream(direct_video_link)
            time.sleep(10)
        else:
            print(f"Could not get final link for {url}. Skipping upload.")
    
    print("\nAutomation process finished.")

if __name__ == "__main__":
    main()
