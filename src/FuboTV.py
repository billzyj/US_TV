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

def scrape_fubo_tv():
    driver = run_webdriver()
    driver.get(FUBO_URL)

    try:
        print("Entering ZIP code...")
        zip_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, ZIP_INPUT_ID))
        )
        driver.execute_script(f"arguments[0].setAttribute('value', '{ZIPCODE}');", zip_input)
        
        all_data = {}

        for plan, plan_id in PACKAGE_CONTAINERS.items():
            print(f"Processing {plan} plan...")

            # Reload the DOM to prevent stale element reference
            driver.refresh()
            time.sleep(1)  # Give time for elements to reload

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
            print("Channels recorded")

            all_data[plan] = pd.DataFrame(channels, columns=["Channel Name"])
            # Re-locate and close the pop-up before moving to the next plan
            close_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//button[@aria-label='{CLOSE_POPUP_BUTTON_ARIA}']"))
            )
            click_button(driver, close_button)
            print("Channel list closed")

        # Save data to excel
        with pd.ExcelWriter(OUTPUT_FILE, engine="xlsxwriter") as writer:
            for plan, df in all_data.items():
                df.to_excel(writer, sheet_name=plan, index=False)
                writer.sheets[plan].freeze_panes(1, 0)

        print(f"FuboTV data saved: {OUTPUT_FILE}")
    
    except Exception as e:
        print(f"ERROR: {e}")

    finally:
        driver.quit()
