import os
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.WebDriverUtils import run_webdriver, OUTPUT_DIR


# VARIABLES FOR FLEXIBILITY
FUBO_URL = "https://fubo.tv/welcome"
ZIPCODE = "79423"
ZIP_INPUT_ID = "react-aria-5"
PACKAGE_CONTAINERS = {
    "Essential": "package-container-us-essential-mo-v1",
    "Pro": "package-container-us-pro",
    "Elite": "package-container-us-elite-v2",
}
LEARN_MORE_BUTTON_CLASS = "details-button css-vya3ut"
SHOW_MORE_BUTTON_CLASS = "css-t5itrl"
CLOSE_POPUP_BUTTON_ARIA = "Close"
IMG_TAG = "img"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "FuboTVChannelList.xlsx")

def scrape_fubo_tv():
    driver = run_webdriver()
    driver.get(FUBO_URL)

    try:
        print("Entering ZIP code...")
        zip_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, ZIP_INPUT_ID)))
        driver.execute_script(f"arguments[0].setAttribute('value', '{ZIPCODE}');", zip_input)
        time.sleep(2)

        all_data = {}

        for plan, plan_id in PACKAGE_CONTAINERS.items():
            print(f"Processing {plan} plan...")
            plan_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f"//div[@data-testid='{plan_id}']"))
            )
            learn_more_button = plan_container.find_element(By.CLASS_NAME, LEARN_MORE_BUTTON_CLASS)
            driver.execute_script("arguments[0].click();", learn_more_button)
            time.sleep(3)

            show_more_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, SHOW_MORE_BUTTON_CLASS))
            )
            driver.execute_script("arguments[0].click();", show_more_button)
            time.sleep(2)

            channels = [
                img.get_attribute("title") for img in driver.find_elements(By.TAG_NAME, IMG_TAG)
            ]
            all_data[plan] = pd.DataFrame(channels, columns=["Channel Name"])

            close_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//button[@aria-label='{CLOSE_POPUP_BUTTON_ARIA}']"))
            )
            driver.execute_script("arguments[0].click();", close_button)

        with pd.ExcelWriter(OUTPUT_FILE, engine="xlsxwriter") as writer:
            for plan, df in all_data.items():
                df.to_excel(writer, sheet_name=plan, index=False)
                writer.sheets[plan].freeze_panes(1, 0)

        print(f"FuboTV data saved: {OUTPUT_FILE}")

    finally:
        driver.quit()
