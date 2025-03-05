import os
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.WebDriverUtils import ZIPCODE, OUTPUT_DIR, load_page, click_element, set_zipcode, write_to_excel

# Variables for flexibility
SLING_URL = "https://www.sling.com/channels"
PLAN_DIV_CLASS = "sc-FQuPU"
IMG_TAG = "img"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "SlingTVChannelList.xlsx")

def scrape_sling_tv(mode="headless"):
    """Scrapes live channel data from SlingTV."""
    driver = load_page(mode, "SlingTV", SLING_URL, check_popup = True, close_locator = (By.XPATH, "//button[@type='reset']"), sleep_time = 1)
    
    try:
        # Locate and click the "Compare Plans" button
        print("Locating Compare Plans button...")
        compare_plans_button = driver.find_element(By.XPATH, "//button[.//p[contains(text(), 'Compare Plans')]]")
        click_element(driver, (By.XPATH, "//button[.//p[contains(text(), 'Compare Plans')]]"))
        print("Opened Compare Plans window...")
        time.sleep(1)
        
        set_zipcode(driver, ZIPCODE, (By.XPATH, "//input[@data-reference-id='billing-form-zip-field']"))

        # Initialize dictionary to store channel data
        all_channels = {}

        # Find all plan name divs dynamically
        plan_name_divs = driver.find_elements(By.CLASS_NAME, PLAN_DIV_CLASS)
        print(f"Found {len(plan_name_divs)} plans.")

        # Process each plan
        for plan_div in plan_name_divs:
            plan_name = plan_div.text.strip()  # Extract plan name
            if not plan_name:
                continue  # Skip if the text is empty

            print(f"Processing plan: {plan_name}...")

            # Locate the next sibling div that contains the channels
            try:
                plan_container = plan_div.find_element(By.XPATH, "following-sibling::div")
                channel_elements = plan_container.find_elements(By.TAG_NAME, "img")

                # Extract all channel names from `img alt` attributes
                channels = [img.get_attribute("alt") for img in channel_elements]
                print(f"Extracted {len(channels)} channels for {plan_name}.")

                # Store channel presence in dictionary
                for channel in channels:
                    if channel not in all_channels:
                        all_channels[channel] = {p_name.text.strip(): "" for p_name in plan_name_divs}

                    all_channels[channel][plan_name] = "✔"  # Mark availability

            except Exception as e:
                print(f"Error extracting channels for {plan_name}: {e}")


        # Convert dictionary to DataFrame
        df_sling_tv = pd.DataFrame.from_dict(all_channels, orient="index").reset_index()
        df_sling_tv.columns = ["Channel Name", "Orange", "Blue", "Both"]

        # Save to Excel
        write_to_excel(df_sling_tv, OUTPUT_FILE, sheet_name="SlingTV Channels")
        # with pd.ExcelWriter(OUTPUT_FILE, engine="xlsxwriter") as writer:
        #     df_sling_tv.to_excel(writer, sheet_name="SlingTV Channels", index=False)
        #     worksheet = writer.sheets["SlingTV Channels"]
        #     worksheet.freeze_panes(1, 0)  # Freeze the first row
        #     worksheet.autofilter(0, 0, len(df_sling_tv), len(df_sling_tv.columns) - 1)  # Enable filtering

        # print(f"Excel file saved successfully: {OUTPUT_FILE}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        driver.quit()