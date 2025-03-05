import os
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.WebDriverUtils import ZIPCODE, OUTPUT_DIR, load_page, click_element, set_zipcode, smooth_scroll_to_bottom, write_to_excel

# Variables for flexibility
DIRECTV_STREAM_URL = "https://streamtv.directv.com/channels/modal/"
SET_ZIP_LINK_ID = "hide-change"
ZIP_INPUT_ID = "zipcode-search"
SET_ZIP_LINK_BUTTON_ARIA_LABEL = "Search ZIP Code"

CHANNELS_TABLE_HEADER_ID = "channels-table-head"
CHANNELS_TABLE_BODY_ID = "nestedTableBody"
CHANNELS_TABLE_ROW_CLASS = "MuiTableRow-root"
CHANNEL_SPAN_CLASS = "MuiTypography-root"
PACKAGES = ["Entertainment", "Choice", "Ultimate", "Premier"]
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "DirecTVStreamChannelList.xlsx")

def scrape_directv_stream(mode="headless"):
    """Scrapes live channel data from DirecTV Stream."""
    driver = load_page(mode, "DirecTV Stream", DIRECTV_STREAM_URL)

    try:
        # Locate and click the zipcode link
        click_element(driver, (By.ID, SET_ZIP_LINK_ID))
        print("Opened set zipcode window...")
        
        # Set zipcode and submit, page will be refreshed
        set_zipcode(driver, ZIPCODE, (By.ID, ZIP_INPUT_ID), (By.XPATH, f"//a[@aria-label='{SET_ZIP_LINK_BUTTON_ARIA_LABEL}']"))

        smooth_scroll_to_bottom(driver)
        
        # Locate the channel table header
        channels_header = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, CHANNELS_TABLE_HEADER_ID))
        )

        # Extract package plans from table header dynamically
        packages = []
        package_headers = channels_header.find_elements(By.TAG_NAME, "th")
        for header in package_headers:
            package_name_elem = header.find_elements(By.CLASS_NAME, "package-name")
            if package_name_elem:
                packages.append(package_name_elem[0].text.strip())

        print(f"Extracted packages: {packages}")

        # Locate the channels container div
        channels_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, CHANNELS_TABLE_BODY_ID))
        )
        print("channel div located")
        # Extract all channel rows within channels_div
        channels = channels_div.find_elements(By.CLASS_NAME, CHANNELS_TABLE_ROW_CLASS)
        print("channels extracted")

        # Extract Channel Name, Number, and Availability in Plans
        all_channels = []
        print(len(channels))
        for channel in channels:
            cells = channel.find_elements(By.TAG_NAME, "td")

            # Extract channel name and number (inside first td)
            channel_info = cells[0].find_elements(By.CLASS_NAME, CHANNEL_SPAN_CLASS)
            #print(channel_info[0].text, " ", channel_info[1].text)
            if len(channel_info) < 2:
                continue  # Skip if information is missing
            channel_name = channel_info[0].text.strip()
            channel_number = channel_info[1].text.strip()

            # Extract package availability (second to fifth td)
            package_status = []
            for i in range(1, len(packages) + 1):
                included = "✔️" if cells[i].find_elements(By.TAG_NAME, "span") else ""
                package_status.append(included)

            # Store data
            all_channels.append([channel_name, channel_number] + package_status)

        # Convert to DataFrame
        df_directv_stream = pd.DataFrame(all_channels, columns=["Channel Name", "Channel Number"] + packages)

        # Sort DataFrame by Channel Name
        df_directv_stream = df_directv_stream.sort_values(by=["Channel Name"])

        # Write to Excel File
        write_to_excel(df_directv_stream, OUTPUT_FILE, sheet_name="DirecTV Stream Channels")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        driver.quit()
