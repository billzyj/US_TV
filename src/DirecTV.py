import os
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.WebDriverUtils import ZIPCODE, OUTPUT_DIR, load_page, click_element, set_zipcode, smooth_scroll_to_bottom, write_to_excel, extract_channel_data

# Variables for flexibility
DIRECTV_URL = "https://www.directv.com/channel-lineup/"
SET_ZIP_LINK_CLASS = "mui-style-11zofoq"
ZIP_INPUT_ID = "zipcode-search"
SET_ZIP_LINK_BUTTON_ARIA_LABEL = "Set ZIP Code"

CHANNELS_TABLE_BODY_ID = "tableBody"
CHANNELS_TABLE_ROW_ID = "tableBodyRow"
TOGGLE_BUTTON_CLASS = "mui-style-1ii9cd9"

CHANNELS_TABLE_HEADER_ID = "tableHeader"
PACKAGE_NAME_CLASS = "MuiTypography-root"
CHANNELS_DIV_ID = "nestedTableBody"
TABLE_ROW_ID = "nestedTableRow"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "DirecTVChannelList.xlsx")

def scrape_directv(mode="headless"):
    """Scrapes live channel data from DirecTV."""
    driver = load_page(mode, "DirecTV", DIRECTV_URL)

    try:
        # Locate and click the zipcode link
        click_element(driver, (By.CLASS_NAME, SET_ZIP_LINK_CLASS))
        print("Opened set zipcode window...")
        
        # Set zipcode and submit, page will be refreshed
        set_zipcode(driver, ZIPCODE, (By.ID, ZIP_INPUT_ID), (By.XPATH, f"//a[@aria-label='{SET_ZIP_LINK_BUTTON_ARIA_LABEL}']"))

        smooth_scroll_to_bottom(driver)
        
        # Locate the channel table header
        channels_header = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, CHANNELS_TABLE_HEADER_ID))
        )
        print(f"Header located")
        # Extract package plans from table header dynamically
        packages = []
        package_headers = channels_header.find_elements(By.TAG_NAME, "th")
        for header in package_headers:
            package_name_elem = header.find_elements(By.CLASS_NAME, PACKAGE_NAME_CLASS)
            if package_name_elem:
                packages.append(package_name_elem[0].text.strip())

        print(f"Extracted packages: {packages}")
        if packages[0] == "CHANNELS":
            packages.pop(0)

        channels = extract_channel_data(driver, (By.ID, CHANNELS_DIV_ID), (By.ID, TABLE_ROW_ID))
        
        # Extract Channel Name, Number, and Availability in Plans
        all_channels = []
        print(len(channels))
        for channel in channels:
            cells = channel.find_elements(By.TAG_NAME, "td")

            # Extract channel name and number (inside first td)
            channel_info = cells[0].find_elements(By.TAG_NAME, "p")
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
        df_directv = pd.DataFrame(all_channels, columns=["Channel Name", "Channel Number"] + packages)

        # Sort DataFrame by Channel Name
        df_directv = df_directv.sort_values(by=["Channel Name"])

        # Write to Excel File
        write_to_excel(df_directv, OUTPUT_FILE, sheet_name="DirecTV Channels")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        driver.quit()