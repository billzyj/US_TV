import os
import time
import re
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.WebDriverUtils import ZIPCODE, OUTPUT_DIR, run_webdriver, click_button, set_zipcode, smooth_scroll_to_bottom

# Variables for flexibility
DIRECTV_URL = "https://www.directv.com/channel-lineup/"
SET_ZIP_LINK_CLASS = "mui-style-11zofoq"
ZIP_INPUT_ID = "zipcode-search"
SET_ZIP_LINK_BUTTON_ARIA_LABEL = "Set ZIP Code"
CHANNELS_TABLE_BODY_ID = "tableBody"
CHANNELS_TABLE_ROW_ID = "tableBodyRow"
TOGGLE_BUTTON_CLASS = "mui-style-1ii9cd9"
CHANNELS_DIV_ID = "nestedTableBody"
TABLE_ROW_ID = "nestedTableRow"
PACKAGES = ["Entertainment", "Choice", "Ultimate", "Premier"]
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "DirecTVChannelList.xlsx")

def scrape_directv(mode="headless"):
    """Scrapes live channel data from DirecTV."""
    print("Web scraping DirecTV...")
    driver = run_webdriver(mode)
    driver.get(DIRECTV_URL)
    print("Waiting for page to load...")

    try:
        # Locate and click the zipcode link
        print("Locating set zipcode link...")
        set_zip_link = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CLASS_NAME, SET_ZIP_LINK_CLASS))
        )
        click_button(driver, set_zip_link)
        print("Opened set zipcode window...")
        
        # Set zipcode and submit, page will be refreshed
        set_zipcode(driver, ZIPCODE, zip_input_id=ZIP_INPUT_ID)

        set_zipcode_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//a[@aria-label='{SET_ZIP_LINK_BUTTON_ARIA_LABEL}']"))
        )
        click_button(driver, set_zipcode_button)

        # # Locate the channels table body
        # channels_table_body = WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located((By.ID, CHANNELS_TABLE_BODY_ID))
        # )
        
        # # Locate all rows within the table
        # table_rows = channels_table_body.find_elements(By.XPATH, f"//tr[contains(@id, '{CHANNELS_TABLE_ROW_ID}')]")

        # # Find the last dropdown toggle button (img)
        # dropdown_toggle = table_rows[-1].find_element(By.CLASS_NAME, TOGGLE_BUTTON_CLASS)
        # click_button(driver, dropdown_toggle)
        # print(f"closed add-on channels")

        smooth_scroll_to_bottom(driver)
        
        # Locate the channels container div
        channels_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, CHANNELS_DIV_ID))
        )
        print("channel div located")
        # Extract all channel rows within channels_div
        channels = channels_div.find_elements(By.ID, TABLE_ROW_ID)
        print("channels extracted")

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
            for i in range(1, 5):
                included = "✔️" if cells[i].find_elements(By.TAG_NAME, "span") else ""
                package_status.append(included)

            # Store data
            all_channels.append([channel_name, channel_number] + package_status)

        # Convert to DataFrame
        df_directv = pd.DataFrame(all_channels, columns=["Channel Name", "Channel Number"] + PACKAGES)

        # Sort DataFrame by Channel Name
        df_directv = df_directv.sort_values(by=["Channel Name"])

        # Write to Excel File
        with pd.ExcelWriter(OUTPUT_FILE, engine="xlsxwriter") as writer:
            df_directv.to_excel(writer, sheet_name="DirecTV Channels", index=False)
            worksheet = writer.sheets["DirecTV Channels"]
            worksheet.freeze_panes(1, 0)  # Freeze the first row
            worksheet.autofilter(0, 0, len(df_directv), len(df_directv.columns) - 1)  # Enable sorting for Channel Name

        print(f"Excel file saved successfully: {OUTPUT_FILE}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        driver.quit()
