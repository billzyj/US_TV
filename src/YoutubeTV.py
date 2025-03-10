import os
import re
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.WebDriverUtils import ZIPCODE, OUTPUT_DIR, LOGGER, load_page, click_element, extract_channel_data, write_to_excel

# Variables for flexibility
YOUTUBE_TV_URL = f"https://tv.youtube.com/welcome/?utm_servlet=prod&rd_rsn=asi&zipcode={ZIPCODE}"
SUBMIT_BUTTON_CLASS = "tv-network-browser__input-area-submit"
CHANNELS_DIV_CLASS = "tv-network-matrix__body"
CHANNEL_TAG = "a"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "YoutubeTVChannelList.xlsx")

def scrape_youtube_tv(mode="headless"):
    """Scrapes live channel data from YoutubeTV."""
    driver = load_page(mode, "YoutubeTV", YOUTUBE_TV_URL)
    channel_names = []
    try:
        # Locate and click the submit button to pull channel list
        click_element(driver, (By.CLASS_NAME, SUBMIT_BUTTON_CLASS))
        LOGGER.info("Compare plans window opened successfully.")

        channels = extract_channel_data(driver, (By.CLASS_NAME, CHANNELS_DIV_CLASS), (By.TAG_NAME, CHANNEL_TAG))
        LOGGER.info(f"Extracted {len(channels)} channels for youtube.")

        for channel in channels:
            match = re.findall(r'Button - (.*?) \(all-channels\)', channel.get_attribute("lb-options")) #return list of lists
            if match:
                channel_names.append(match[0]) # Extract only the first matched string

        # Convert data to dataframe
        df_youtube_tv = pd.DataFrame(channel_names, columns=["Channel Name"])

        # Save to excel with formatting
        write_to_excel(df_youtube_tv, OUTPUT_FILE, sheet_name="YoutubeTV Channels")
        return channel_names
    except Exception as e:
        LOGGER.error(f"Error: {e}")

    finally:
        driver.quit()