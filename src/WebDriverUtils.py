import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Output directory
OUTPUT_DIR = "./output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_webdriver():
    """Initialize and return a Selenium WebDriver instance."""
    chrome_options = Options()
    #chrome_options.add_argument("--headless")  # Uncomment for headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

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
