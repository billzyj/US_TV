import os
import time
import re
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.WebDriverUtils import ZIPCODE, OUTPUT_DIR, run_webdriver, click_button, set_zipcode

# Variables for flexibility
DIRECTV_STREAM_URL = "https://streamtv.directv.com/stream-packages/"
SEE_ALL_CHANNELS_LINK_ID = "plancard-card-0-see-all-channels-cta"
CHANGE_ZIPCODE_LINK_CLASS = "mui-style-1d7v3j3"
ZIP_INPUT_CLASS = "mui-style-16sx77j"
UPDATE_ZIP_BUTTON_CLASS = "mui-style-159jcxx"
POP_UP_WINDOW_DIV_CLASS = "mui-style-2leisg"
CHANNELS_TABLE_ID = "channelLineup-channel-grid"
CHANNELS_TABLE_HEADERS_ID = "channels-table-head"
CHANNELS_TABLE_BODY_ID = "tableBody"
CHANNELS_TABLE_ROW_CLASS = "nestedTableRow"
PACKAGES = ["Entertainment", "Choice", "Ultimate", "Premier"]
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "DirecTVChannelList.xlsx")

def scrape_directv(mode="headless"):
    """Scrapes live channel data from DirecTV."""
    print("Web scraping DirecTV...")
    driver = run_webdriver(mode)
    driver.get(DIRECTV_STREAM_URL)
    print("Waiting for page to load...")

    try:
        # Locate and click the see all channels link
        print("Locating see all channels link...")
        see_all_channels_link = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, SEE_ALL_CHANNELS_LINK_ID))
        )
        click_button(driver, see_all_channels_link)
        print("Opened channels lineup pop up window...")
        time.sleep(1)
        
        # Locate and click the change zipcode link
        print("Locating change zipcode link...")
        change_zipcode_link = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CLASS_NAME, CHANGE_ZIPCODE_LINK_CLASS))
        )
        click_button(driver, change_zipcode_link)
        print("Setting zipcode...")
    
        # Set zipcode and update, channels will be refreshed in the popup window
        set_zipcode(driver, ZIPCODE, zip_class=ZIP_INPUT_CLASS)

        update_zipcode_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, UPDATE_ZIP_BUTTON_CLASS))
        )
        click_button(driver, update_zipcode_button)

        # TODO 1: Scroll down to the bottom of pop up page to load all channels

        # TODO 2: Extract package plans from table header
        packages = []
        # TODO 3: Extract Channel Name, Number, and Availability in Plans from table rows


        # TODO 4: Write to Excel File


    except Exception as e:
        print(f"Error: {e}")

    finally:
        driver.quit()
