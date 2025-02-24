import os
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.WebDriverUtils import ZIPCODE, OUTPUT_DIR, run_webdriver, click_button, set_zipcode

# Variables for flexibility
SLING_URL = "https://www.sling.com/channels"
COMPARE_BUTTON_CLASS = "bCdbqq"
ZIP_CLASS = "sc-hokXgN"
PLAN_DIV_CLASSES = {
    "Orange": "zRktI",
    "Blue": "hZrsXy",
    "Both": "hRtvzv",
}
IMG_TAG = "img"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "SlingTVChannelList.xlsx")

def scrape_sling_tv(mode="headless"):
    print("Web scraping SlingTV...")
    driver = run_webdriver(mode)
    driver.get(SLING_URL)
    print("Waiting for page to load...")
    #time.sleep(1)  # Allow JavaScript execution

    try:
        print("Checking for promotion pop-up...")
        try:
            # Locate pop-up close button
            close_popup_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='reset']"))
            )
            click_button(driver, close_popup_button)
            print("Closed promotion pop-up.")
            time.sleep(2)
        except:
            print("No pop-up found, proceeding.")

        # Locate and click the "Compare Plans" button
        print("Locating Compare Plans button...")
        compare_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CLASS_NAME, COMPARE_BUTTON_CLASS))
        )
        click_button(driver, compare_button)
        print("Opened Compare Plans window...")
        time.sleep(1)
        
        set_zipcode(driver, ZIPCODE, zip_class=ZIP_CLASS)

        # Initialize dictionary to store channel data
        all_channels = {}

        for plan, plan_class in PLAN_DIV_CLASSES.items():
            print(f"Processing {plan} plan...")

            # Locate the unique container div
            unique_div = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, plan_class))
            )

            # Locate the next sibling div that actually contains the channels
            plan_container = unique_div.find_element(By.XPATH, "following-sibling::div")

            # Extract all channels from `img alt` attributes
            channels = [
                img.get_attribute("alt") for img in plan_container.find_elements(By.TAG_NAME, IMG_TAG)
            ]
            print(f"Extracted {len(channels)} channels for {plan}.")

            # Store channel presence in dictionary
            for channel in channels:
                if channel not in all_channels:
                    all_channels[channel] = {plan_key: "" for plan_key in PLAN_DIV_CLASSES.keys()}

                # Mark corresponding column with √
                all_channels[channel][plan] = "√"
                
                if plan != "Both":
                    all_channels[channel]["Both"] = "√"

        # Convert dictionary to DataFrame
        df_sling_tv = pd.DataFrame.from_dict(all_channels, orient="index").reset_index()
        df_sling_tv.columns = ["Channel Name", "Orange", "Blue", "Both"]

        # Save to Excel
        with pd.ExcelWriter(OUTPUT_FILE, engine="xlsxwriter") as writer:
            df_sling_tv.to_excel(writer, sheet_name="SlingTV Channels", index=False)
            worksheet = writer.sheets["SlingTV Channels"]
            worksheet.freeze_panes(1, 0)  # Freeze the first row

        print(f"Excel file saved successfully: {OUTPUT_FILE}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        driver.quit()

    