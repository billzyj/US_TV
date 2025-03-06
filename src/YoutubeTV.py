import os
import re
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.WebDriverUtils import ZIPCODE, OUTPUT_DIR, load_page, click_element, write_to_excel

# Variables for flexibility
YOUTUBE_TV_URL = f"https://tv.youtube.com/welcome/?utm_servlet=prod&rd_rsn=asi&zipcode={ZIPCODE}"
ZIPCODE = "79423"
MODAL_SELECTOR = "tv-network-browser-matrix"
CONTENT_DIV_CLASS = "tv-network-matrix__body"
COMPARE_BUTTON_CLASS = "tv-network-browser__input-area-submit"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "YoutubeTVChannelList.xlsx")

def scrape_youtube_tv(mode="headless"):
    """Scrapes live channel data from YoutubeTV."""
    driver = load_page(mode, "YoutubeTV", YOUTUBE_TV_URL)
    
    try:
        print("Waiting for youtube page to load...")
        time.sleep(1)  # Allow JavaScript execution

        # Locate and click the compare plans button
        click_element(driver, (By.CLASS_NAME, COMPARE_BUTTON_CLASS))
        print("Compare plans window opened successfully.")

        # Wait for channel list to load in modal
        print("Waiting for channel list to load...")
        WebDriverWait(driver, 30).until(
            lambda d: d.execute_script(f"""
                let modal = document.querySelector('{MODAL_SELECTOR}');
                return modal && modal.innerText.trim().length > 0;
            """)
        )
        print("Channel list loaded successfully.")

        # Extract channel content using JavaScript
        modal_content = driver.execute_script(f"""
            let modal = document.querySelector('{MODAL_SELECTOR}');
            return modal ? modal.innerHTML : 'Not Found';
        """)
        
        # If content is not found, exit script
        if modal_content == "Not Found" or modal_content.strip() == "":
            print("Error: Channel list not found.")
            driver.quit()
            exit()

        # Extract channel names from inner html
        channel_names = re.findall(r'Button - (.*?) \(all-channels\)', modal_content)
        print(f"Extracted {len(channel_names)} channels from YouTube TV.")

        # Convert data to dataframe
        df_youtube_tv = pd.DataFrame(channel_names, columns=["Channel Name"])

        # Save to excel with formatting
        write_to_excel(df_youtube_tv, OUTPUT_FILE, sheet_name="YoutubeTV Channels")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        driver.quit()