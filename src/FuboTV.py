import os
import time
import re
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.WebDriverUtils import run_webdriver, OUTPUT_DIR, click_button


# Variables for flexibility
FUBO_URL = "https://fubo.tv/welcome"
ZIPCODE = "79423"
ZIP_INPUT_ID = "react-aria-5"
PACKAGE_CONTAINERS = {
    "Essential": "package-container-us-essential-mo-v1",
    "Pro": "package-container-us-pro",
    "Elite": "package-container-us-elite-v2",
}
LEARN_MORE_BUTTON_CLASS = "details-button"
SHOW_MORE_BUTTON_CLASS = "css-t5itrl"
CHANNEL_DIV_CLASS = ".css-1tqzony"
IMG_TAG = "img"
CLOSE_POPUP_BUTTON_ARIA = "Close"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "FuboTVChannelList.xlsx")
print("Web scraping FuboTV...")

def set_zipcode(driver):
    """Ensures the correct ZIP code is set before loading channel data."""
    print("Setting ZIP code...")
    zip_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, ZIP_INPUT_ID))
    )
    driver.execute_script(f"""
        arguments[0].value = '{ZIPCODE}'; 
        arguments[0].dispatchEvent(new Event('input'));
    """, zip_input)

    time.sleep(2)  # Allow JavaScript to update content
    print("ZIP code set successfully.")

def scrape_fubo_tv():
    driver = run_webdriver()
    driver.get(FUBO_URL)

    try:        
        all_channels = {}

        for plan, plan_id in PACKAGE_CONTAINERS.items():
            print(f"Processing {plan} plan...")

            # Reload the DOM to prevent stale element reference
            driver.refresh()
            time.sleep(1)  # Give time for elements to reload

            set_zipcode(driver)

            # Re-locate plan container to prevent stale element reference
            plan_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f"//div[@data-testid='{plan_id}']"))
            )

            # Re-locate the "Learn More" button before clicking
            learn_more_button = plan_container.find_element(By.CLASS_NAME, LEARN_MORE_BUTTON_CLASS)
            click_button(driver, learn_more_button)
            time.sleep(1)
            print("Learn more button clicked")

            # Re-locate the "Show More" button before clicking
            show_more_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, SHOW_MORE_BUTTON_CLASS))
            )
            click_button(driver, show_more_button)
            time.sleep(1)
            print("Show more button clicked")

            # Extract channel content using JavaScript
            modal_content = driver.execute_script(f"""
                let modal = document.querySelector('{CHANNEL_DIV_CLASS}');
                return modal ? modal.innerHTML : 'Not Found';
            """)
            
            # If content is not found, exit script
            if modal_content == "Not Found" or modal_content.strip() == "":
                print("Error: Channel list not found.")
                driver.quit()
                exit()

            # Extract channel names from inner html
            channels = set(re.findall(r'title="([^"]+)"', modal_content))
            print(f"Extracted {len(channels)} channels for {plan}.")

            # Store channel presence in dictionary
            for channel in channels:
                if channel not in all_channels:
                    all_channels[channel] = {plan_key: "" for plan_key in PACKAGE_CONTAINERS.keys()}  # Dynamic keys
                all_channels[channel][plan] = "✔"

            # Re-locate and close the pop-up before moving to the next plan
            close_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//button[@aria-label='{CLOSE_POPUP_BUTTON_ARIA}']"))
            )
            click_button(driver, close_button)
            print("Channel list closed")

        # Convert dictionary to DataFrame
        df_fubo_tv = pd.DataFrame.from_dict(all_channels, orient="index").reset_index()
        df_fubo_tv.columns = ["Channel Name"] + list(PACKAGE_CONTAINERS.keys())

        # Save to Excel in a single sheet
        with pd.ExcelWriter(OUTPUT_FILE, engine="xlsxwriter") as writer:
            df_fubo_tv.to_excel(writer, sheet_name="FuboTV Channels", index=False)
            worksheet = writer.sheets["FuboTV Channels"]
            worksheet.freeze_panes(1, 0)  # Freeze the first row
            worksheet.autofilter(0, 0, len(df_fubo_tv), len(df_fubo_tv.columns) - 1)  # Sort only "Channel Name"
            
        print(f"Excel file saved successfully: {OUTPUT_FILE}")
    
    except Exception as e:
        print(f"ERROR: {e}")

    finally:
        driver.quit()
