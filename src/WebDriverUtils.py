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
from selenium.webdriver.common.action_chains import ActionChains
import random
import time

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
        # Locate pop-up close button
        close_popup_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(close_locator)
        )
        click_button(driver, close_popup_button)
        print("Closed promotion pop-up.")
        time.sleep(1)
    except:
        print("No pop-up found, proceeding.")
    return driver

def click_button(driver, button):
    try:
        """Ensure the button is clickable by scrolling into view and clicking via JavaScript."""
        driver.execute_script("arguments[0].scrollIntoView();", button)  # Scroll to button
        time.sleep(1)  # Give time for scrolling animation
        driver.execute_script("arguments[0].click();", button)  # Click using JS
    except Exception as e:
        print(f"Error: {e}")

def set_zipcode(driver, zipcode, locator):
    print("Setting ZIP code...")

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
    return zip_input
    # zip_input.clear()
    # # Set the ZIP code and trigger JavaScript input events
    # driver.execute_script(f"""
    #     arguments[0].value = '{zipcode}'; 
    #     arguments[0].dispatchEvent(new Event('input'));
    # """, zip_input)

# def set_zipcode(driver, zipcode, input_locator, submit_locator=None):
#     """Sets the ZIP code and submits if required."""
#     try:
#         zip_input = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located(input_locator)
#         )
#         zip_input.clear()
#         zip_input.send_keys(zipcode)
#         time.sleep(1)

#         if submit_locator:
#             submit_button = WebDriverWait(driver, 5).until(
#                 EC.element_to_be_clickable(submit_locator)
#             )
#             click_button(driver, submit_button)

#         print(f"ZIP code {zipcode} set successfully.")
#     except Exception as e:
#         print(f"Error setting ZIP code: {e}")

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

def extract_channel_data(driver, container_locator, channel_locator, img_attr="title"):
    """Extracts channel names from a given container."""
    try:
        container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(container_locator)
        )
        channels = container.find_elements(By.CLASS_NAME, channel_locator)
        return [ch.get_attribute(img_attr).strip() for ch in channels if ch.get_attribute(img_attr)]
    except Exception as e:
        print(f"Error extracting channels: {e}")
        return []
    
def write_to_excel(df, output_file, sheet_name="Channels"):
    """Writes a DataFrame to an Excel file with formatting."""
    with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
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