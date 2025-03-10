import os
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.WebDriverUtils import ZIPCODE, OUTPUT_DIR, LOGGER, load_page, click_element, set_zipcode, extract_channel_data, smooth_scroll_to_bottom, write_to_excel

# Variables for flexibility
DIRECTV_STREAM_URL = "https://streamtv.directv.com/channels/modal/"
SET_ZIP_LINK_ID = "hide-change"
ZIP_INPUT_ID = "zipcode-search"
SET_ZIP_LINK_BUTTON_ARIA_LABEL = "Search ZIP Code"

CHANNELS_TABLE_HEADER_ID = "channels-table-head"
PLAN_NAME_CLASS = "package-name"
CHANNELS_TABLE_BODY_ID = "nestedTableBody"
CHANNELS_TABLE_ROW_CLASS = "MuiTableRow-root"
CHANNEL_SPAN_CLASS = "MuiTypography-root"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "DirecTVStreamChannelList.xlsx")

def scrape_directv_stream(mode="headless"):
    """Scrapes live channel data from DirecTV Stream."""
    driver = load_page(mode, "DirecTV Stream", DIRECTV_STREAM_URL)
    all_channels, plans = [], []
    try:
        # Locate and click the zipcode link
        click_element(driver, (By.ID, SET_ZIP_LINK_ID))
        LOGGER.info("Opened set zipcode window...")
        
        # Set zipcode and submit, page will be refreshed
        set_zipcode(driver, ZIPCODE, (By.ID, ZIP_INPUT_ID), (By.XPATH, f"//a[@aria-label='{SET_ZIP_LINK_BUTTON_ARIA_LABEL}']"))

        smooth_scroll_to_bottom(driver)
        
        # Locate the channel table header
        channels_header = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, CHANNELS_TABLE_HEADER_ID))
        )
        LOGGER.info(f"Header located")
        # Extract plans from table header dynamically
        plan_headers = channels_header.find_elements(By.TAG_NAME, "th")
        for header in plan_headers:
            plan_name_elem = header.find_elements(By.CLASS_NAME, PLAN_NAME_CLASS)
            if plan_name_elem:
                plans.append(plan_name_elem[0].text.strip())
        LOGGER.info(f"Extracted plans: {plans}")

        channels = extract_channel_data(driver, (By.ID, CHANNELS_TABLE_BODY_ID), (By.CLASS_NAME, CHANNELS_TABLE_ROW_CLASS))
        LOGGER.info(f"Extracted {len(channels)} channels for DirecTV Stream.")

        # Extract Channel Name, Number, and Availability in Plans
        LOGGER.info(len(channels))
        for channel in channels:
            cells = channel.find_elements(By.TAG_NAME, "td")

            # Extract channel name and number (inside first td)
            channel_info = cells[0].find_elements(By.CLASS_NAME, CHANNEL_SPAN_CLASS)
            if len(channel_info) < 2:
                continue  # Skip if information is missing
            channel_name = channel_info[0].text.strip()
            channel_number = channel_info[1].text.strip()

            # Extract plan availability (second to fifth td)
            plan_status = []
            for i in range(1, len(plans) + 1):
                included = "✔️" if cells[i].find_elements(By.TAG_NAME, "span") else ""
                plan_status.append(included)

            # Store data
            all_channels.append([channel_name, channel_number] + plan_status)

        # Convert to DataFrame
        df_directv_stream = pd.DataFrame(all_channels, columns=["Channel Name", "Channel Number"] + plans)

        # Sort DataFrame by Channel Name
        df_directv_stream = df_directv_stream.sort_values(by=["Channel Name"])

        # Write to Excel File
        write_to_excel(df_directv_stream, OUTPUT_FILE, sheet_name="DirecTV Stream Channels")

    except Exception as e:
        LOGGER.error(f"Error: {e}")

    finally:
        driver.quit()
        return all_channels, plans