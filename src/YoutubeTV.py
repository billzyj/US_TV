import os
import re
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# Variables
zipcode = "79423"
url = f"https://tv.youtube.com/welcome/?utm_servlet=prod&rd_rsn=asi&zipcode={zipcode}"
submit_button_class = "tv-network-browser__input-area-submit"  # Class of the submit button
modal_selector = "tv-network-browser-matrix"  # Alias for the modal container
content_div_class = "tv-network-matrix__body"  # Class of the div containing the channel list

# Define output directories
output_dir = "./output"
output_file = os.path.join(output_dir, "YoutubeTVChannelList.xls")

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Setup Selenium WebDriver options
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Run headless mode (uncomment when debugging is done)
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

# Use WebDriver Manager to automatically download the correct ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Load the YouTube TV webpage
driver.get(url)

try:
    # Wait for input box and set ZIP code
    print("Entering ZIP code...")
    zip_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, ZIP_INPUT_ID)))
    driver.execute_script(f"arguments[0].setAttribute('placeholder', '{ZIPCODE}');", zip_input)
    driver.execute_script(f"arguments[0].setAttribute('value', '{ZIPCODE}');", zip_input)
    time.sleep(2)  # Give time for page to react

    # Initialize Data Storage
    all_data = {}

    for plan, plan_id in PACKAGE_CONTAINERS.items():
        print(f"Processing {plan} plan...")

        # Locate plan container and click "Learn More"
        plan_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//div[@data-testid='{plan_id}']"))
        )
        learn_more_button = plan_container.find_element(By.CLASS_NAME, LEARN_MORE_BUTTON_CLASS)
        driver.execute_script("arguments[0].click();", learn_more_button)  # Mimic user click
        print(f"Opened {plan} plan details...")

        # Click "Show More" to load full list
        show_more_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, SHOW_MORE_BUTTON_CLASS))
        )
        driver.execute_script("arguments[0].click();", show_more_button)
        print("Loaded full channel list...")

        # Extract all channels from `img` title attributes
        time.sleep(2)  # Give time for images to load
        channels = [
            img.get_attribute("title") for img in driver.find_elements(By.TAG_NAME, IMG_TITLE_TAG)
        ]
        print(f"Extracted {len(channels)} channels for {plan}.")

        # Store data in dictionary
        all_data[plan] = pd.DataFrame(channels, columns=["Channel Name"])

        # Close pop-up window to return to main page
        close_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[@aria-label='{CLOSE_POPUP_BUTTON_ARIA}']"))
        )
        driver.execute_script("arguments[0].click();", close_button)
        print(f"Closed {plan} details window.")

    # Save all plans into a single Excel file with separate sheets
    with pd.ExcelWriter(OUTPUT_FILE, engine="xlsxwriter") as writer:
        for plan, df in all_data.items():
            df.to_excel(writer, sheet_name=plan, index=False)
            worksheet = writer.sheets[plan]
            worksheet.freeze_panes(1, 0)  # Freeze the first row

    print(f"Excel file saved: {OUTPUT_FILE}")

except Exception as e:
    print(f"Error: {e}")

finally:
    driver.quit()
