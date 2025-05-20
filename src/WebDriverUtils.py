import logging
import sys
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
import concurrent.futures
from src.config import load_config
import logging.handlers
from typing import List, Dict, Any, Optional
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
import atexit
import psutil

# Load configuration
config = load_config()
ZIPCODE = config["ZIPCODE"]
OUTPUT_DIR = config["OUTPUT_DIR"]
os.makedirs(OUTPUT_DIR, exist_ok=True)

LOG_FILE = os.path.join(OUTPUT_DIR, "tv_scraper.log")

# Global variable to store active ChromeDriver instances
_active_drivers = set()

def cleanup_chrome_drivers():
    """Clean up all ChromeDriver processes."""
    for driver in _active_drivers:
        try:
            driver.quit()
        except Exception as e:
            LOGGER.error(f"Error quitting driver: {e}")
    _active_drivers.clear()
    
    # Kill any remaining ChromeDriver processes
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if 'chromedriver' in proc.info['name'].lower():
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

# Register cleanup function to run at exit
atexit.register(cleanup_chrome_drivers)

def setup_logger():
    """Setup logging with UTF-8 encoding and prevent duplicate handlers."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Remove any existing handlers (prevents duplicate logging)
    logger.handlers.clear()

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)  # Console shows INFO+
    console_formatter = logging.Formatter("%(levelname)s - %(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Rotating File Handler (Force UTF-8 Encoding)
    file_handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=10485760, backupCount=5, encoding="utf-8")
    file_handler.setLevel(logging.INFO)  # Log all levels to file
    file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger
LOGGER = setup_logger() # Initialize logger

def setup_chrome_options(mode: str) -> Options:
    """Setup Chrome options based on the specified mode."""
    chrome_options = Options()
    if mode.lower() == "headless":
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-accelerated-2d-canvas")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--use-gl=disabled")
        chrome_options.add_argument("--disable-gpu-compositing")
        chrome_options.add_argument("--use-gl=swiftshader")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    return chrome_options

def run_webdriver(mode: str = "headless") -> WebDriver:
    """Initialize and return a Selenium WebDriver instance.

    Parameters:
        mode (str): The mode to run the WebDriver in. Options are 'headless' or 'gui'.

    Returns:
        WebDriver: A configured Selenium WebDriver instance.

    Raises:
        Exception: If there is an error initializing the WebDriver.
    """
    try:
        chrome_options = setup_chrome_options(mode)
        LOGGER.info(f"Starting WebDriver in {'Headless' if 'headless' in mode else 'GUI'} mode...")
        
        # Initialize ChromeDriver with default version
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Add driver to active set
        _active_drivers.add(driver)
        
        return driver
    except Exception as e:
        LOGGER.error(f"Failed to initialize WebDriver: {e}")
        cleanup_chrome_drivers()  # Clean up any partial initialization
        raise

def load_page(mode: str, page_name: str, page_url: str, check_popup: bool = False, close_locator: Optional[tuple] = None, sleep_time: int = 0) -> WebDriver:
    """Load a web page using the specified WebDriver mode.

    Parameters:
        mode (str): The mode to run the WebDriver in.
        page_name (str): A descriptive name for the page being loaded.
        page_url (str): The URL of the page to load.
        check_popup (bool): Whether to check for and handle popups.
        close_locator (Optional[tuple]): Locator for the popup close button.
        sleep_time (int): Time to wait after loading the page.

    Returns:
        WebDriver: The WebDriver instance after loading the page.

    Raises:
        Exception: If there is an error loading the page.
    """
    LOGGER.info(f"Web scraping {page_name}...")
    driver = None
    try:
        driver = run_webdriver(mode)
        driver.get(page_url)
        LOGGER.info("Waiting for page to load...")
        time.sleep(sleep_time)
        if check_popup:
            driver = handle_popup(driver, close_locator)
        return driver
    except Exception as e:
        LOGGER.error(f"Error loading page {page_name}: {e}")
        if driver:
            try:
                driver.quit()
                _active_drivers.discard(driver)
            except:
                pass
        raise

def handle_popup(driver: WebDriver, close_locator: Optional[tuple]) -> WebDriver:
    """Handle any popup that appears on the page.

    Parameters:
        driver (WebDriver): The WebDriver instance.
        close_locator (Optional[tuple]): Locator for the popup close button.

    Returns:
        WebDriver: The WebDriver instance after handling the popup.

    Raises:
        Exception: If there is an error handling the popup.
    """
    LOGGER.info("Checking for promotion pop-up...")
    try:
        click_element(driver, close_locator)
        LOGGER.info("Closed promotion pop-up.")
    except:
        LOGGER.exception("No pop-up found, proceeding.")
    return driver

def click_element(driver: WebDriver, element_locator: tuple, element_container: Optional[WebElement] = None) -> None:
    """Click an element on the page.

    Parameters:
        driver (WebDriver): The WebDriver instance.
        element_locator (tuple): Locator for the element to click.
        element_container (Optional[WebElement]): Container element if the element is nested.

    Raises:
        Exception: If there is an error clicking the element.
    """
    try:
        # Locate element
        if element_container:
            element = element_container.find_element(element_locator[0], element_locator[1])
        else:
            element = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable(element_locator)
            )
        LOGGER.info("Element located")
        driver.execute_script("arguments[0].scrollIntoView();", element)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", element)
    except Exception as e:
        LOGGER.error(f"Error: {e}")

def set_zipcode(driver: WebDriver, zipcode: str, input_locator: tuple, submit_locator: Optional[tuple] = None) -> Optional[WebElement]:
    """Set the ZIP code in the input field and submit if required.

    Parameters:
        driver (WebDriver): The WebDriver instance.
        zipcode (str): The ZIP code to set.
        input_locator (tuple): Locator for the ZIP input field.
        submit_locator (Optional[tuple]): Locator for the submit button.

    Returns:
        Optional[WebElement]: The ZIP input element if successful, None otherwise.

    Raises:
        Exception: If there is an error setting the ZIP code.
    """
    try:
        LOGGER.info("Setting ZIP code...")
        zip_input = WebDriverWait(driver, 15).until(EC.presence_of_element_located(input_locator))
        LOGGER.info("Located ZIP input field")
        driver.execute_script("arguments[0].scrollIntoView();", zip_input)
        driver.execute_script("arguments[0].focus();", zip_input)
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
                submit_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(submit_locator))
                click_element(driver, submit_button)
            except:
                LOGGER.info("Submit button not found or not needed.")
        time.sleep(1)
        LOGGER.info(f"ZIP code {zipcode} set successfully.")
        return zip_input
    except Exception as e:
        LOGGER.error(f"Error setting ZIP code: {e}")
        return None

def smooth_scroll_to_bottom(driver: WebDriver, scroll_step: int = 1000, wait_time: float = 0.1) -> None:
    """Smoothly scroll from the top to the bottom of the page.

    Parameters:
        driver (WebDriver): The WebDriver instance.
        scroll_step (int): Pixels per scroll step.
        wait_time (float): Time to wait after each scroll.

    Raises:
        Exception: If there is an error scrolling the page.
    """
    LOGGER.info("Resetting scroll position to the top...")
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(0.1)
    total_height = driver.execute_script("return document.body.scrollHeight")
    current_position = 0
    LOGGER.info(f"Starting smooth scroll to bottom... (Total Height: {total_height}px)")
    while current_position < 2 * total_height:
        current_position += scroll_step
        driver.execute_script(f"window.scrollTo(0, {current_position});")
        time.sleep(wait_time)  # Allow content to load smoothly

    LOGGER.info("Finished scrolling to the bottom.")

def extract_channel_data(driver: WebDriver, container_locator: tuple, channel_locator: tuple) -> List[WebElement]:
    """Extract channel names from a given container.

    Parameters:
        driver (WebDriver): The WebDriver instance.
        container_locator (tuple): Locator for the container element.
        channel_locator (tuple): Locator for the channel elements.

    Returns:
        List[WebElement]: A list of channel elements.

    Raises:
        Exception: If there is an error extracting channel data.
    """
    try:
        container = WebDriverWait(driver, 10).until(EC.presence_of_element_located(container_locator))
        LOGGER.info("channel container div located")
        channels = container.find_elements(channel_locator[0], channel_locator[1])
        return channels
    except Exception as e:
        LOGGER.error(f"Error extracting channels: {e}")
        return []

def write_to_excel(df, output_file, sheet_name="Sheet1", index=True):
    """Write DataFrame to Excel file."""
    try:
        # Ensure file has .xlsx extension
        if not output_file.endswith('.xlsx'):
            output_file = output_file + '.xlsx'
            
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=index)
            
            # Get workbook and worksheet objects
            workbook = writer.book
            worksheet = writer.sheets[sheet_name]
            
            # Add some formatting
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'bg_color': '#D9E1F2',
                'border': 1
            })
            
            # Write the column headers with the defined format
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num + (1 if index else 0), value, header_format)
                
            # Adjust column widths
            for i, col in enumerate(df.columns):
                max_len = max(
                    df[col].astype(str).apply(len).max(),
                    len(col)
                )
                worksheet.set_column(i + (1 if index else 0), i + (1 if index else 0), max_len + 2)
                
        LOGGER.info(f"Successfully wrote data to {output_file}")
        return True
    except Exception as e:
        LOGGER.error(f"Error writing to Excel: {str(e)}")
        return False

def write_to_csv(df: pd.DataFrame, output_file: str, index: bool = False) -> None:
    """Write a DataFrame to a CSV file.

    Parameters:
        df (pd.DataFrame): The DataFrame to write.
        output_file (str): The path to the output CSV file.
        index (bool): Whether to include the index in the output.

    Raises:
        Exception: If there is an error writing to the CSV file.
    """
    df.to_csv(output_file, index=index)
    LOGGER.info(f"Data saved to {output_file}")

def move_mouse_randomly(driver: WebDriver) -> None:
    """Move the mouse randomly on the page to simulate human interaction.

    Parameters:
        driver (WebDriver): The WebDriver instance.

    Raises:
        Exception: If there is an error moving the mouse.
    """
    actions = ActionChains(driver)
    for _ in range(random.randint(5, 10)):
        x_offset = random.randint(-20, 20)
        y_offset = random.randint(-20, 20)
        actions.move_by_offset(x_offset, y_offset).perform()
        time.sleep(random.uniform(0.1, 0.5))

def parallel_scrape(scrapers):
    """Run multiple scrapers in parallel using concurrent.futures.

    Parameters:
        scrapers: A list of tuples, each containing (scraper_function, mode).

    Returns:
        A list of results from each scraper.

    Raises:
        Exception: If there is an error in parallel scraping.
    """
    results = []
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:  # Limit concurrent scrapers
            futures = [executor.submit(scraper, mode) for scraper, mode in scrapers]
            for future in concurrent.futures.as_completed(futures):
                try:
                    results.append(future.result())
                    LOGGER.info(f"Scraper {results.index(future.result())} completed.")
                except Exception as e:
                    LOGGER.error(f"Error in parallel scraping: {e}")
    finally:
        cleanup_chrome_drivers()  # Ensure cleanup after parallel scraping
        LOGGER.info(f"Parallel Scraping Completed.")
    return results

def retry_operation(operation, max_retries: int = 3, delay: float = 1.0):
    """Retry a given operation a specified number of times."""
    for attempt in range(max_retries):
        try:
            return operation()
        except Exception as e:
            if attempt == max_retries - 1:
                LOGGER.error(f"Operation failed after {max_retries} attempts: {e}")
                raise
            LOGGER.warning(f"Attempt {attempt + 1} failed, retrying...")
            time.sleep(delay)