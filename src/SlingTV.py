import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# Variables for flexibility
SLING_URL = "https://www.sling.com/channels"
COMPARE_BUTTON_CLASS = "sc-kcbnda gFLBJo sc-kNBZmU dFLigJ"
PLAN_DIV_CLASSES = {
    "Orange": "sc-esExBO fmSNeb",
    "Blue": "sc-esExBO fmSNeb",
    "Both": "sc-esExBO fmSNeb",
}
IMG_TAG = "img"
OUTPUT_DIR = "./output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "Sling.xls")

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Setup Selenium WebDriver options
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Run in headless mode (uncomment for debugging)
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

# Use WebDriver Manager to automatically download the correct ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Load the SlingTV webpage
driver.get(SLING_URL)

try:
    print("Waiting for page to load...")
    time.sleep(5)  # Allow JavaScript execution

    # Locate and click the "Compare Plans" button
    print("Locating Compare Plans button...")
    compare_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, COMPARE_BUTTON_CLASS))
    )
    driver.execute_script("arguments[0].click();", compare_button)  # Mimic user click
    print("Opened Compare Plans window...")

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
