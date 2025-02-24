import os
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.WebDriverUtils import ZIPCODE, OUTPUT_DIR, run_webdriver, click_button, set_zipcode

# Variables for flexibility
HULU_URL = "https://www.hulu.com/welcome"
VIEW_CHANNELS_BUTTON_CLASS = "Billboard__modalLink"
ZIP_INPUT_ID = "zipcode-input"
ZIP_SUBMIT_CLASS = "submit-button"
CHANNEL_DIV_CLASSES = "channels-container"
SPAN_CLASS = "NetworkIcon__network-name-invisible"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "HuluTVChannelList.xlsx")

def scrape_hulu_tv(mode="headless"):
    print("Web scraping HuluTV...")
    driver = run_webdriver(mode)
    driver.get(HULU_URL)
    print("Waiting for page to load...")
    #time.sleep(1)  # Allow JavaScript execution

    try:
        # Locate and click the "View Channels" button
        print("Locating View Channels button...")
        channel_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CLASS_NAME, VIEW_CHANNELS_BUTTON_CLASS))
        )
        click_button(driver, channel_button)
        print("Opened Channel Plans window...")
        time.sleep(1)
        
        # Set to specified zipcode
        set_zipcode(driver, ZIPCODE, zip_input_id=ZIP_INPUT_ID)
        channel_submit_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CLASS_NAME, ZIP_SUBMIT_CLASS))
        )
        click_button(driver, channel_submit_button)

        # Locate the unique container div
        channels_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, CHANNEL_DIV_CLASSES))
        )

        # Extract all span elements containing channel names
        channel_elements = channels_div.find_elements(By.CLASS_NAME, SPAN_CLASS)

        # Extract the text from each span element
        channel_names = [span.get_attribute("innerText").strip() for span in channel_elements]

        # Convert data to dataframe
        df_hulu_tv = pd.DataFrame(channel_names, columns=["Channel Name"])

        # Save to excel with formatting
        with pd.ExcelWriter(OUTPUT_FILE, engine="xlsxwriter") as writer:
            df_hulu_tv.to_excel(writer, sheet_name="Hulu TV Channels", index=False)
            worksheet = writer.sheets["Hulu TV Channels"]
            worksheet.freeze_panes(1, 0)  # Freeze the first row

        print(f"Excel file saved successfully: {OUTPUT_FILE}")


    except Exception as e:
        print(f"Error: {e}")

    finally:
        driver.quit()

    