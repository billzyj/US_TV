import os
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.WebDriverUtils import ZIPCODE, OUTPUT_DIR, LOGGER, extract_channel_data, load_page, click_element, set_zipcode, write_to_excel

# Variables for flexibility
HULU_URL = "https://www.hulu.com/welcome"
VIEW_CHANNELS_BUTTON_CLASS = "Billboard__modalLink"
ZIP_INPUT_ID = "zipcode-input"
ZIP_SUBMIT_CLASS = "submit-button"
CHANNELS_DIV_CLASS = "channels-container"
SPAN_CLASS = "NetworkIcon__network-name-invisible"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "HuluTVChannelList.xlsx")

def scrape_hulu_tv(mode="headless"):
    """Scrapes live channel data from HuluTV."""
    driver = load_page(mode, "HuluTV", HULU_URL)

    try:
        # Locate and click the "View Channels" button
        click_element(driver, (By.CLASS_NAME, VIEW_CHANNELS_BUTTON_CLASS))
        LOGGER.info("Opened Channel Plans window...")
        
        # Set to specified zipcode
        set_zipcode(driver, ZIPCODE, (By.ID, ZIP_INPUT_ID), (By.CLASS_NAME, ZIP_SUBMIT_CLASS))

        channels = extract_channel_data(driver, (By.CLASS_NAME, CHANNELS_DIV_CLASS), (By.CLASS_NAME, SPAN_CLASS))
        LOGGER.info(f"Extracted {len(channels)} channels for HuluTV.")

        # Extract the text from each span element
        channel_names = [span.get_attribute("innerText").strip() for span in channels]

        # Convert data to dataframe
        df_hulu_tv = pd.DataFrame(channel_names, columns=["Channel Name"])

        # Save to excel with formatting
        write_to_excel(df_hulu_tv, OUTPUT_FILE, sheet_name="HuluTV Channels")
        return channel_names
    except Exception as e:
        LOGGER.error(f"Error: {e}")

    finally:
        driver.quit()