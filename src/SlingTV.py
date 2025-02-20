import os
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.WebDriverUtils import run_webdriver, OUTPUT_DIR, click_button

# Variables for flexibility
SLING_URL = "https://www.sling.com/channels"
COMPARE_BUTTON_CLASS = "sc-kcbnda"
PLAN_DIV_CLASSES = {
    "Orange": "sc-esExBO fmSNeb",
    "Blue": "sc-esExBO fmSNeb",
    "Both": "sc-esExBO fmSNeb",
}
IMG_TAG = "img"
OUTPUT_DIR = "./output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "SlingTVChannelList.xls")

def scrape_sling_tv():
    driver = run_webdriver()
    driver.get(SLING_URL)
    print("Waiting for page to load...")
    time.sleep(2)  # Allow JavaScript execution

    try:
        print("Checking for promotion pop-up...")
        try:
            # Locate pop-up close button
            close_popup_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='reset']"))
            )
            click_button(driver, close_popup_button)
            print("Closed promotion pop-up.")
            time.sleep(1)
        except:
            print("No pop-up found, proceeding.")

        # Locate and click the "Compare Plans" button
        print("Locating Compare Plans button...")
        compare_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, COMPARE_BUTTON_CLASS))
        )
        click_button(driver, compare_button)
        print("Opened Compare Plans window...")
        time.sleep(1)

        # Initialize dictionary to store channel data
        all_channels = {}

        for plan, plan_class in PLAN_DIV_CLASSES.items():
            print(f"Processing {plan} plan...")

            # Locate plan container
            plan_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, plan_class))
            )

            # Extract all channels from `img alt` attributes
            channels = [
                img.get_attribute("alt") for img in plan_container.find_elements(By.TAG_NAME, IMG_TAG)
            ]
            print(f"Extracted {len(channels)} channels for {plan}.")

            # Store channel presence in dictionary
            for channel in channels:
                if channel not in all_channels:
                    all_channels[channel] = {"Orange": "", "Blue": "", "Both": ""}

                # Mark corresponding column with ✅
                all_channels[channel][plan] = "✅"

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

    