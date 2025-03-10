import os
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.WebDriverUtils import ZIPCODE, OUTPUT_DIR, LOGGER, load_page, click_element, set_zipcode, extract_channel_data, write_to_excel

# Variables for flexibility
FUBO_URL = "https://fubo.tv/welcome"
ZIP_INPUT_ID = "react-aria-5"
PLAN_CONTAINERS = {
#    "Essential": "package-container-us-essential-mo-v1",
    "Pro": "package-container-us-pro",
    "Elite": "package-container-us-elite-v2",
}
LEARN_MORE_BUTTON_CLASS = "details-button"
SHOW_MORE_BUTTON_CLASS = "css-t5itrl"
CHANNELS_DIV_CLASS = "css-1tqzony"
CHANNEL_CLASS = "css-d9cqmo"
IMG_TAG = "img"
CLOSE_POPUP_BUTTON_ARIA = "Close"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "FuboTVChannelList.xlsx")

def scrape_fubo_tv(mode="headless"):
    """Scrapes live channel data from FuboTV."""
    driver = load_page(mode, "FuboTV", FUBO_URL)
    all_channels = {}
    try:        
        for plan, plan_id in PLAN_CONTAINERS.items():
            LOGGER.info(f"Processing {plan} plan...")

            # Reload the DOM to prevent stale element reference
            driver.refresh()

            set_zipcode(driver, ZIPCODE, (By.ID, ZIP_INPUT_ID))

            # Re-locate plan container to prevent stale element reference
            plan_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f"//div[@data-testid='{plan_id}']"))
            )

            # Re-locate the "Learn More" button before clicking
            click_element(driver, (By.CLASS_NAME, LEARN_MORE_BUTTON_CLASS), plan_container)
            #click_element(driver, (By.XPATH, f"//button[@aria-label='Learn more']"), plan_container)
            LOGGER.info("Learn more button clicked")

            # Re-locate the "Show More" button before clicking
            click_element(driver, (By.CLASS_NAME, SHOW_MORE_BUTTON_CLASS))
            LOGGER.info("Show more button clicked")

            channels = extract_channel_data(driver, (By.CLASS_NAME, CHANNELS_DIV_CLASS), (By.CLASS_NAME, CHANNEL_CLASS))
            LOGGER.info(f"Extracted {len(channels)} channels for {plan}.")

            # Store channel presence in dictionary
            for channel in channels:
                try:
                    img_element = channel.find_element(By.TAG_NAME, "img")
                    # Extract only the name after "-"
                    channel_name = img_element.get_attribute('title')

                    # Store channel in dictionary (mark available in this package)
                    if channel_name not in all_channels:
                        all_channels[channel_name] = {pkg: "" for pkg in PLAN_CONTAINERS.keys()}  # Initialize row
                    all_channels[channel_name][plan] = "✔️"  # Mark availability
                except Exception as e:
                    LOGGER.info(f"Error extracting channel name: {e}")

            # Re-locate and close the pop-up before moving to the next plan
            close_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//button[@aria-label='{CLOSE_POPUP_BUTTON_ARIA}']"))
            )
            click_element(driver, close_button)
            LOGGER.info("Channel list closed")

        # Convert dictionary to DataFrame
        df_fubo_tv = pd.DataFrame.from_dict(all_channels, orient="index").reset_index()
        df_fubo_tv.columns = ["Channel Name"] + list(PLAN_CONTAINERS.keys())

        # Save to Excel in a single sheet
        write_to_excel(df_fubo_tv, OUTPUT_FILE, sheet_name="FuboTV Channels")
    
    except Exception as e:
        LOGGER.error(f"ERROR: {e}")

    finally:
        driver.quit()
        return all_channels, PLAN_CONTAINERS.keys()
