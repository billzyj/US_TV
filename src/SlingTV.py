import os
import pandas as pd
from selenium.webdriver.common.by import By
from src.WebDriverUtils import ZIPCODE, OUTPUT_DIR, LOGGER, load_page, click_element, set_zipcode, extract_channel_data, write_to_excel

# Variables for flexibility
SLING_URL = "https://www.sling.com/channels"
PLAN_CONTAINERS = {
    "Orange" : "Only on Sling Orange",
    "Blue" : "Only on Sling Blue",
    "Both" : "Available in All Base Services"
 }
IMG_TAG = "img"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "SlingTVChannelList.xlsx")

def scrape_sling_tv(mode="headless"):
    """Scrapes live channel data from SlingTV."""
    driver = load_page(mode, "SlingTV", SLING_URL, check_popup = True, close_locator = (By.XPATH, "//button[@type='reset']"), sleep_time = 1)
    all_channels = {}
    try:
        # Locate and click the "Compare Plans" button
        LOGGER.info("Locating Compare Plans button...")
        click_element(driver, (By.XPATH, "//button[.//p[contains(text(), 'Compare Plans')]]"))
        LOGGER.info("Opened Compare Plans window...")
        
        set_zipcode(driver, ZIPCODE, (By.XPATH, "//input[@data-reference-id='billing-form-zip-field']"))

        # Initialize dictionary to store channel data
        for plan_name, plan_div in PLAN_CONTAINERS.items():
            channels = extract_channel_data(driver, (By.XPATH, f"//div[contains(text(), '{plan_div}')]/following-sibling::*"), (By.TAG_NAME, "img"))

            try:
                # Extract all channel names from `img alt` attributes
                channel_names = [img.get_attribute("alt") for img in channels]
                LOGGER.info(f"Extracted {len(channel_names)} channels for {plan_name}.")

                # Store channel presence in dictionary
                for channel in channel_names:
                    if channel not in all_channels:
                        all_channels[channel] = {p_name: "" for p_name in PLAN_CONTAINERS.keys()}

                    all_channels[channel][plan_name] = "✔️"  # Mark availability

            except Exception as e:
                LOGGER.info(f"Error extracting channels for {plan_name}: {e}")

        # ✅ NEW: Update "Both" Plan
        for channel, plans in all_channels.items():
            if plans["Orange"] == "✔️" or plans["Blue"] == "✔️":
                all_channels[channel]["Both"] = "✔️"

        # Convert dictionary to DataFrame
        df_sling_tv = pd.DataFrame.from_dict(all_channels, orient="index").reset_index()
        df_sling_tv.columns = ["Channel Name", "Orange", "Blue", "Both"]

        # Save to Excel
        write_to_excel(df_sling_tv, OUTPUT_FILE, sheet_name="SlingTV Channels")

    except Exception as e:
        LOGGER.error(f"Error: {e}")

    finally:
        driver.quit()
        return all_channels, PLAN_CONTAINERS.keys()