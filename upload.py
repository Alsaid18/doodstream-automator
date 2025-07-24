import os
import requests
import time
from playwright.sync_api import sync_playwright

# --- Configuration ---
# The API key is securely retrieved from GitHub's Secrets.
API_KEY = os.getenv("DOODSTREAM_API_KEY") 
URL_FILE = "urls.txt"
# DoodStream API endpoint for remote upload
UPLOAD_API_URL = f"https://doodapi.co/api/upload/url?key={API_KEY}&url="

def get_direct_link(page_url: str):
    """Navigates to the DoodStream page and extracts the final direct link after the timer."""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            print(f"Navigating to page: {page_url}")
            page.goto(page_url, timeout=90000)

            # This is the crucial part: find the download button and click it.
            # The text might vary, so we look for something containing "Download".
            download_button = page.locator('a:has-text("Download")').first
            if download_button.is_visible():
                print("Download button found. Clicking it...")
                download_button.click()
            else:
                print("Could not find the initial download button.")
                browser.close()
                return None
            
            # Wait for the timer to finish and the final link to appear.
            # The real download link is often inside an element with class 'download-content'.
            final_link_selector = ".download-content a"
            print("Waiting for the final download link to appear...")
            final_link_element = page.locator(final_link_selector)
            
            # Wait for the element to become visible, with a timeout
            final_link_element.wait_for(timeout=30000)

            direct_link = final_link_element.get_attribute('href')
            print(f"SUCCESS: Found direct link: {direct_link}")
            browser.close()
            return direct_link
    except Exception as e:
        print(f"An error occurred while getting direct link for {page_url}: {e}")
        if 'browser' in locals() and browser.is_connected():
            browser.close()
        return None

def upload_to_doodstream(direct_url: str):
    """Sends the direct link to the DoodStream API to start the upload."""
    if not direct_url:
        print("No direct URL provided, skipping upload.")
        return

    print(f"Requesting remote upload for: {direct_url}")
    try:
        response = requests.get(UPLOAD_API_URL + direct_url, timeout=60)
        if response.status_code == 200:
            print(f"API call successful. DoodStream is now processing the video.")
            print("API Response:", response.json())
        else:
            print(f"Error calling DoodStream API. Status: {response.status_code}, Response: {response.text}")
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
        direct_video_link = get_direct_link(url)
        if direct_video_link:
            upload_to_doodstream(direct_video_link)
            # Add a small delay between API calls to be safe
            time.sleep(5)
        else:
            print(f"Could not get direct link for {url}. Skipping upload.")
    
    print("\nAutomation process finished.")

if __name__ == "__main__":
    main()
