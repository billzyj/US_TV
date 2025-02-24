import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Output directory
ZIPCODE = "79423"
OUTPUT_DIR = "./output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_webdriver(mode="headless"):
    """Initialize and return a Selenium WebDriver instance.

    - Default mode is headless.
    - If 'gui' is passed, it runs in traditional mode (with browser UI).
    """
    chrome_options = Options()

    if mode.lower() == "headless":
        chrome_options.add_argument("--headless=new")  # Improved headless mode
        chrome_options.add_argument("--disable-gpu")  # Needed for headless stability
        chrome_options.add_argument("--window-size=1920,1080")  # Ensure consistent UI loading

    # Common options
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")  # Prevent crashes on some systems

    print(f"Starting WebDriver in {'Headless' if 'headless' in mode else 'GUI'} mode...")

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def click_button(driver, button):
    try:
        """Ensure the button is clickable by scrolling into view and clicking via JavaScript."""
        driver.execute_script("arguments[0].scrollIntoView();", button)  # Scroll to button
        time.sleep(1)  # Give time for scrolling animation
        driver.execute_script("arguments[0].click();", button)  # Click using JS
    except Exception as e:
        print(f"Error: {e}")

def set_zipcode(driver, zipcode, zip_input_id=None, zip_class=None):
    """Ensures the correct ZIP code is set before loading channel data.
    
    - Tries `zip_input_id` first if provided.
    - Falls back to `zip_class` if `zip_input_id` is not available.
    """

    print("Setting ZIP code...")

    if not zip_input_id and not zip_class:
        raise ValueError("You must provide either zip_input_id or zip_class.")
    
    # Determine locator strategy dynamically
    if zip_input_id:
        locator = (By.ID, zip_input_id)
    elif zip_class:
        locator = (By.CLASS_NAME, zip_class)
    else:
        raise ValueError("Both zip_input_id and zip_class cannot be None. Provide at least one.")

    # Wait for the ZIP input field to appear
    zip_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(locator)
    )

    print("Located ZIP input field")

        # Select all and delete existing text (to avoid stale values)
    zip_input.send_keys(Keys.CONTROL + "a")  # Select all
    zip_input.send_keys(Keys.BACKSPACE)  # Clear input

    # Simulate typing character by character
    for char in zipcode:
        zip_input.send_keys(char)
        time.sleep(0.1)  # Simulates real typing speed

    print("ZIP code typed successfully.")

    # zip_input.clear()
    # # Set the ZIP code and trigger JavaScript input events
    # driver.execute_script(f"""
    #     arguments[0].value = '{zipcode}'; 
    #     arguments[0].dispatchEvent(new Event('input'));
    # """, zip_input)

    # time.sleep(1)  # Allow JavaScript to update content
    # print("ZIP code set successfully.")
