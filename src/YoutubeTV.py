import os
import re
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.WebDriverUtils import ZIPCODE, OUTPUT_DIR, extract_channel_data, load_page, click_element, write_to_excel

# Variables for flexibility
YOUTUBE_TV_URL = f"https://tv.youtube.com/welcome/?utm_servlet=prod&rd_rsn=asi&zipcode={ZIPCODE}"
SUBMIT_BUTTON_CLASS = "tv-network-browser__input-area-submit"
CHANNELS_DIV_CLASS = "tv-network-matrix__body"
CHANNEL_TAG = "a"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "YoutubeTVChannelList.xlsx")

def scrape_youtube_tv(mode="headless"):
    """Scrapes live channel data from YoutubeTV."""
    driver = load_page(mode, "YoutubeTV", YOUTUBE_TV_URL)
    
    try:
        # Locate and click the submit button to pull channel list
        click_element(driver, (By.CLASS_NAME, SUBMIT_BUTTON_CLASS))
        print("Compare plans window opened successfully.")

        # Wait for channel list to load in modal
        print("Waiting for channel list to load...")
        channels = extract_channel_data(driver, (By.CLASS_NAME, CHANNELS_DIV_CLASS), (By.TAG_NAME, CHANNEL_TAG))

        channel_names = []
        for channel in channels:
            channel_names.append(re.findall(r'Button - (.*?) \(all-channels\)', channel.get_attribute("lb-options")))

        # Convert data to dataframe
        df_youtube_tv = pd.DataFrame(channel_names, columns=["Channel Name"])

        # Save to excel with formatting
        write_to_excel(df_youtube_tv, OUTPUT_FILE, sheet_name="YoutubeTV Channels")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        driver.quit()