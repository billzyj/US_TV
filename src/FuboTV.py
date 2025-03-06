import os
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.WebDriverUtils import ZIPCODE, OUTPUT_DIR, load_page, click_element, set_zipcode, write_to_excel

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

    try:        
        all_channels = {}

        for plan, plan_id in PLAN_CONTAINERS.items():
            print(f"Processing {plan} plan...")

            # Reload the DOM to prevent stale element reference
            driver.refresh()
            time.sleep(1)  # Give time for elements to reload

            set_zipcode(driver, ZIPCODE, (By.ID, ZIP_INPUT_ID))
            time.sleep(1)

            # Re-locate plan container to prevent stale element reference
            plan_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f"//div[@data-testid='{plan_id}']"))
            )

            # Re-locate the "Learn More" button before clicking
            click_element(driver, (By.CLASS_NAME, LEARN_MORE_BUTTON_CLASS), plan_container)
            #click_element(driver, (By.XPATH, f"//button[@aria-label='Learn more']"), plan_container)
            time.sleep(1)
            print("Learn more button clicked")

            # Re-locate the "Show More" button before clicking
            click_element(driver, (By.CLASS_NAME, SHOW_MORE_BUTTON_CLASS))
            time.sleep(1)
            print("Show more button clicked")

            channels_div = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, CHANNELS_DIV_CLASS))
            )
            # Extract channel names
            channels = channels_div.find_elements(By.CLASS_NAME, CHANNEL_CLASS)
            print(f"Extracted {len(channels)} channels for {plan}.")

            # Store channel presence in dictionary
            for channel in channels:
                try:
                    img_element = channel.find_element(By.TAG_NAME, "img")
                    # Extract only the name after "-"
                    channel_name = img_element.get_attribute('title')

                    # Store channel in dictionary (mark available in this package)
                    if channel_name not in all_channels:
                        all_channels[channel_name] = {pkg: "" for pkg in PLAN_CONTAINERS.keys()}  # Initialize row
                    all_channels[channel_name][plan] = "✔"  # Mark availability
                except Exception as e:
                    print(f"Error extracting channel name: {e}")

            # Re-locate and close the pop-up before moving to the next plan
            close_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//button[@aria-label='{CLOSE_POPUP_BUTTON_ARIA}']"))
            )
            click_element(driver, close_button)
            print("Channel list closed")

        # Convert dictionary to DataFrame
        df_fubo_tv = pd.DataFrame.from_dict(all_channels, orient="index").reset_index()
        df_fubo_tv.columns = ["Channel Name"] + list(PLAN_CONTAINERS.keys())

        # Save to Excel in a single sheet
        write_to_excel(df_fubo_tv, OUTPUT_FILE, sheet_name="FuboTV Channels")
        # with pd.ExcelWriter(OUTPUT_FILE, engine="xlsxwriter") as writer:
        #     df_fubo_tv.to_excel(writer, sheet_name="FuboTV Channels", index=False)
        #     worksheet = writer.sheets["FuboTV Channels"]
        #     worksheet.freeze_panes(1, 0)  # Freeze the first row
        #     worksheet.autofilter(0, 0, len(df_fubo_tv), len(df_fubo_tv.columns) - 1)  # Sort only "Channel Name"
            
        # print(f"Excel file saved successfully: {OUTPUT_FILE}")
    
    except Exception as e:
        print(f"ERROR: {e}")

    finally:
        driver.quit()
