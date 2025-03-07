import os
import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# Shared variables
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
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    print(f"Starting WebDriver in {'Headless' if 'headless' in mode else 'GUI'} mode...")

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def load_page(mode, page_name, page_url, check_popup = False, close_locator = None, sleep_time = 0):
    print(f"Web scraping {page_name}...")
    driver = run_webdriver(mode)
    driver.get(page_url)
    print("Waiting for page to load...")
    time.sleep(sleep_time)
    if check_popup :
        driver = handle_popup(driver, close_locator)
    return driver

def handle_popup(driver, close_locator):
    print("Checking for promotion pop-up...")
    try:
        click_element(driver, close_locator)
        print("Closed promotion pop-up.")
        time.sleep(1)
    except:
        print("No pop-up found, proceeding.")
    return driver

def click_element(driver, element_locator, element_container = None):
    try:
        # Locate element
        if element_container:
            element = element_container.find_element(element_locator[0], element_locator[1])
        else :
            element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(element_locator)
            )
        """Ensure the button is clickable by scrolling into view and clicking via JavaScript."""
        driver.execute_script("arguments[0].scrollIntoView();", element)  # Scroll to button
        time.sleep(1)  # Give time for scrolling animation
        driver.execute_script("arguments[0].click();", element)  # Click using JS
    except Exception as e:
        print(f"Error: {e}")

def set_zipcode(driver, zipcode, input_locator, submit_locator=None):
    """Sets the ZIP code and submits if required."""
    try:
        print("Setting ZIP code...")

        # Wait for the ZIP input field to appear
        zip_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(input_locator)
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

        if submit_locator:
            submit_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(submit_locator)
            )
            click_element(driver, submit_button)

        print(f"ZIP code {zipcode} set successfully.")
    except Exception as e:
        print(f"Error setting ZIP code: {e}")
    return zip_input

def smooth_scroll_to_bottom(driver, scroll_step=1000, wait_time=0.25):
    """
    Smoothly scrolls from top to bottom in steps, even if document.body.scrollHeight is fixed.
    
    Parameters:
        driver: Selenium WebDriver instance.
        scroll_step: Pixels per scroll step (default: 1000px).
        wait_time: Time to wait after each scroll (default: 0.5s).
    """
    
    print("Resetting scroll position to the top...")
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(0.1)  # Allow the page to adjust

    # Get the total scroll height
    total_height = driver.execute_script("return document.body.scrollHeight")
    current_position = 0  # Track the current scroll position

    print(f"Starting smooth scroll to bottom... (Total Height: {total_height}px)")

    while current_position < 2 * total_height:
        current_position += scroll_step
        driver.execute_script(f"window.scrollTo(0, {current_position});")
        time.sleep(wait_time)  # Allow content to load smoothly

    print("Finished scrolling to the bottom.")

def extract_channel_data(driver, container_locator, channel_locator):
    """Extracts channel names from a given container."""
    try:
        # Locate the channels container div
        container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(container_locator)
        )
        print("channel container div located")
        # Extract all channel rows within channels_div
        channels = container.find_elements(channel_locator[0], channel_locator[1])
        print("channels extracted")
        return channels
    except Exception as e:
        print(f"Error extracting channels: {e}")
        return []
    
def write_to_excel(df, output_file, sheet_name="Channels", index=False):
    """Writes a DataFrame to an Excel file with formatting."""
    with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name=sheet_name, index = index)
        worksheet = writer.sheets[sheet_name]
        worksheet.freeze_panes(1, 0)
        worksheet.autofilter(0, 0, len(df), len(df.columns) - 1)
    print(f"Data saved to {output_file}")


def move_mouse_randomly(driver):
    actions = ActionChains(driver)
    for _ in range(random.randint(5, 10)):
        x_offset = random.randint(-20, 20)
        y_offset = random.randint(-20, 20)
        actions.move_by_offset(x_offset, y_offset).perform()
        time.sleep(random.uniform(0.1, 0.5))