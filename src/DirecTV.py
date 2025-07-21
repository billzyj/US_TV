import os
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.WebDriverUtils import ZIPCODE, OUTPUT_DIR, LOGGER, load_page, click_element, set_zipcode, extract_channel_data, smooth_scroll_to_bottom, write_to_excel

# Variables for flexibility
DIRECTV_URL = "https://www.directv.com/channel-lineup/"
SET_ZIP_LINK_CLASS = "mui-style-1c87emg"
ZIP_INPUT_ID = "zipcode-search"
SET_ZIP_LINK_BUTTON_ARIA_LABEL = "Update ZIP Code for Local & Regional Channels"

CHANNELS_TABLE_HEADER_ID = "ChannelLineup-PackagesHeader"
PLAN_NAME_CLASS = "MuiTypography-root"
CHANNELS_TABLE_BODY_ID = "tableBody"
CHANNELS_TABLE_ROW_CLASS = "mui-style-1ybie8h"

OUTPUT_FILE = os.path.join(OUTPUT_DIR, "DirecTVChannelList.xlsx")

def scrape_directv(mode="headless"):
    """Scrapes live channel data from DirecTV."""
    driver = load_page(mode, "DirecTV", DIRECTV_URL, sleep_time = 1)
    all_channels, plans = [], []
    try:
        # Locate and click the zipcode link
        click_element(driver, (By.CLASS_NAME, SET_ZIP_LINK_CLASS))
        LOGGER.info("Opened set zipcode window...")
        
        # Set zipcode and submit, page will be refreshed
        set_zipcode(driver, ZIPCODE, (By.ID, ZIP_INPUT_ID), (By.XPATH, f"//a[@aria-label='{SET_ZIP_LINK_BUTTON_ARIA_LABEL}']"))

        smooth_scroll_to_bottom(driver)
        
        # Locate the channel table header
        channels_header = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, CHANNELS_TABLE_HEADER_ID))
        )
        LOGGER.info(f"Header located")
        # Extract plan plans from table header dynamically

        plan_headers = channels_header.find_elements(By.TAG_NAME, "td")
        for header in plan_headers:
            plan_name_elem = header.find_elements(By.CLASS_NAME, PLAN_NAME_CLASS)
            if plan_name_elem:
                plans.append(plan_name_elem[0].text.strip())
        if plans[0] == "CHANNELS":
            plans.pop(0)
        LOGGER.info(f"Extracted plans: {plans}")

        channels = extract_channel_data(driver, (By.ID, CHANNELS_TABLE_BODY_ID), (By.CLASS_NAME, CHANNELS_TABLE_ROW_CLASS))
        LOGGER.info(f"Extracted {len(channels)} channels for DirecTV.")

        for channel in channels:
            # The first child div contains channel info
            info_div = channel.find_elements(By.XPATH, './div')[0]
            channel_name = info_div.find_elements(By.TAG_NAME, "p")[0].text.strip()
            channel_number = info_div.find_elements(By.TAG_NAME, "p")[1].text.strip()

            # The next divs correspond to plan columns
            plan_status = []
            for i in range(1, len(plans) + 1):
                plan_div = channel.find_elements(By.XPATH, f'./div[{i+1}]')[0]
                included = "✔️" if plan_div.find_elements(By.TAG_NAME, "span") and plan_div.find_elements(By.TAG_NAME, "img") else ""
                plan_status.append(included)

            all_channels.append([channel_name, channel_number] + plan_status)

        # Convert to DataFrame
        df_directv = pd.DataFrame(all_channels, columns=["Channel Name", "Channel Number"] + plans)

        # Sort DataFrame by Channel Name
        df_directv = df_directv.sort_values(by=["Channel Name"])

        # Write to Excel File
        write_to_excel(df_directv, OUTPUT_FILE, sheet_name="DirecTV Channels")

    except Exception as e:
        LOGGER.error(f"Error: {e}")

    finally:
        driver.quit()
        return all_channels, plans