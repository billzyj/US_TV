import logging
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
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# Shared variables
ZIPCODE = "79423"
OUTPUT_DIR = "./output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

LOG_FILE = os.path.join(OUTPUT_DIR, "tv_scraper.log")
def setup_logger():
    """Setup logging for the project."""
    logging.basicConfig(
        filename=LOG_FILE,  # Log output to a file
        filemode="a",  # Append logs to the file
        format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
        level=logging.DEBUG  # Capture all logs (DEBUG and above)
    )
    logger = logging.getLogger(__name__)

    # Also log to console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # Only show INFO+ logs in console
    formatter = logging.Formatter("%(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
LOGGER = setup_logger() # Initialize logger

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
        chrome_options.add_argument("--disable-software-rasterizer")  # Avoids software rendering issues
        chrome_options.add_argument("--disable-dev-shm-usage")  # Helps with shared memory issues
        chrome_options.add_argument("--disable-accelerated-2d-canvas")  
        chrome_options.add_argument("--disable-extensions")  
        chrome_options.add_argument("--disable-logging")  
        chrome_options.add_argument("--use-gl=disabled")  # Fully disable OpenGL/WebGL
        chrome_options.add_argument("--disable-gpu-compositing")  # Ensures no GPU rendering
        chrome_options.add_argument("--use-gl=swiftshader")  # Ensure software rendering

    # Common options
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")  # Prevent crashes on some systems
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    LOGGER.info(f"Starting WebDriver in {'Headless' if 'headless' in mode else 'GUI'} mode...")

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def load_page(mode, page_name, page_url, check_popup = False, close_locator = None, sleep_time = 0):
    LOGGER.info(f"Web scraping {page_name}...")
    driver = run_webdriver(mode)
    driver.get(page_url)
    LOGGER.info("Waiting for page to load...")
    time.sleep(sleep_time)
    if check_popup :
        driver = handle_popup(driver, close_locator)
    return driver

def handle_popup(driver, close_locator):
    LOGGER.info("Checking for promotion pop-up...")
    try:
        click_element(driver, close_locator)
        LOGGER.info("Closed promotion pop-up.")
    except:
        LOGGER.exception("No pop-up found, proceeding.")
    return driver

def click_element(driver, element_locator, element_container = None):
    try:
        # Locate element
        if element_container:
            element = element_container.find_element(element_locator[0], element_locator[1])
        else :
            element = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable(element_locator)
            )
        LOGGER.info("Element located")
        """Ensure the button is clickable by scrolling into view and clicking via JavaScript."""
        driver.execute_script("arguments[0].scrollIntoView();", element)  # Scroll to button
        time.sleep(1)  # Give time for scrolling animation
        driver.execute_script("arguments[0].click();", element)  # Click using JS
    except Exception as e:
        LOGGER.error(f"Error: {e}")

def set_zipcode(driver, zipcode, input_locator, submit_locator=None):
    """Sets the ZIP code and submits if required."""
    try:
        LOGGER.info("Setting ZIP code...")

        # Wait for the ZIP input field to appear
        zip_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(input_locator)
        )

        LOGGER.info("Located ZIP input field")

        # Ensure the field is interactable, use JS if necessary
        driver.execute_script("arguments[0].scrollIntoView();", zip_input)
        driver.execute_script("arguments[0].focus();", zip_input)

        # If normal input fails, force input with JavaScript
        if not zip_input.is_enabled():
            LOGGER.info("ZIP input not interactable, using JavaScript...")
            driver.execute_script(f"arguments[0].value = '{zipcode}';", zip_input)
        else:
            # Clear and type ZIP normally
            zip_input.send_keys(Keys.CONTROL + "a")  # Select all
            zip_input.send_keys(Keys.BACKSPACE)  # Clear input
            for char in zipcode:
                zip_input.send_keys(char)
                time.sleep(0.1)  # Simulate real typing
            LOGGER.info("ZIP code typed successfully.")

         # Handle submit button if available
        if submit_locator:
            try:
                submit_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(submit_locator)
                )
                click_element(driver, submit_button)
            except:
                LOGGER.info("Submit button not found or not needed.")
        time.sleep(1)
        LOGGER.info(f"ZIP code {zipcode} set successfully.")
        return zip_input  # Ensure it returns the correct value
    
    except Exception as e:
        LOGGER.error(f"Error setting ZIP code: {e}")
        return None

def smooth_scroll_to_bottom(driver, scroll_step=1000, wait_time=0.25):
    """
    Smoothly scrolls from top to bottom in steps, even if document.body.scrollHeight is fixed.
    
    Parameters:
        driver: Selenium WebDriver instance.
        scroll_step: Pixels per scroll step (default: 1000px).
        wait_time: Time to wait after each scroll (default: 0.5s).
    """
    
    LOGGER.info("Resetting scroll position to the top...")
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(0.1)  # Allow the page to adjust

    # Get the total scroll height
    total_height = driver.execute_script("return document.body.scrollHeight")
    current_position = 0  # Track the current scroll position

    LOGGER.info(f"Starting smooth scroll to bottom... (Total Height: {total_height}px)")

    while current_position < 2 * total_height:
        current_position += scroll_step
        driver.execute_script(f"window.scrollTo(0, {current_position});")
        time.sleep(wait_time)  # Allow content to load smoothly

    LOGGER.info("Finished scrolling to the bottom.")

def extract_channel_data(driver, container_locator, channel_locator):
    """Extracts channel names from a given container."""
    try:
        # Locate the channels container div
        container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(container_locator)
        )
        LOGGER.info("channel container div located")
        # Extract all channel rows within channels_div
        channels = container.find_elements(channel_locator[0], channel_locator[1])
        return channels
    except Exception as e:
        LOGGER.error(f"Error extracting channels: {e}")
        return []
    
def write_to_excel(df, output_file, sheet_name="Channels", index=False):
    """Writes a DataFrame to an Excel file with formatting."""
    with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name=sheet_name, index = index)
        
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]

        # ✅ Freeze First Row & First Column
        worksheet.freeze_panes(1, 1)

       # ✅ Enable Wrap Text Formatting for All Cells
        wrap_format = workbook.add_format({"text_wrap": True})

        # ✅ Set Column Widths
        worksheet.set_column(0, 0, 25, wrap_format)  # First column width
        worksheet.set_column(1, len(df.columns) - 1, 10, wrap_format)  # Other columns width

        # ✅ Wrap Text for First Row (Headers)
        header_format = workbook.add_format({"bold": True, "text_wrap": True, "align": "center", "valign": "vcenter"})
        for col_num, col_name in enumerate(df.columns):
            worksheet.write(0, col_num, col_name, header_format)

        # ✅ Apply Autofilter
        worksheet.autofilter(0, 0, len(df), len(df.columns) - 1)
        
    LOGGER.info(f"Data saved to {output_file}")


def move_mouse_randomly(driver):
    actions = ActionChains(driver)
    for _ in range(random.randint(5, 10)):
        x_offset = random.randint(-20, 20)
        y_offset = random.randint(-20, 20)
        actions.move_by_offset(x_offset, y_offset).perform()
        time.sleep(random.uniform(0.1, 0.5))