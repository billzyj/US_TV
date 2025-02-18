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
    print("Waiting for page to load...")
    time.sleep(3)  # Allow JavaScript execution

    # Click the "Submit" button to load the channels
    print("Locating Submit button...")
    submit_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.CLASS_NAME, submit_button_class))
    )
    driver.execute_script("arguments[0].click();", submit_button)
    print("Clicked Submit button. Waiting for channels to load...")

    # Wait until `tv-network-browser-matrix` contains text
    WebDriverWait(driver, 30).until(
        lambda d: d.execute_script("""
            let modal = document.querySelector('tv-network-browser-matrix');
            return modal && modal.innerText.trim().length > 0;
        """)
    )
    print("Channels loaded!")

    # Extract content using JavaScript
    modal_content = driver.execute_script("""
        let modal = document.querySelector('tv-network-browser-matrix');
        return modal ? modal.innerHTML : 'Not Found';
    """)
    #print("Extracted modal content:", modal_content)

    # If content is empty, exit
    if modal_content == "Not Found" or modal_content.strip() == "":
        print("Error: Modal content not found.")
        driver.quit()
        exit()

    # Extract channel names using regex
    channel_names = re.findall(r'Button - (.*?) \(all-channels\)', modal_content)

    # Convert to DataFrame
    df_youtube_tv = pd.DataFrame(channel_names, columns=["Channel Name"])

    # Save to Excel
    with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
        df_youtube_tv.to_excel(writer, sheet_name="YouTube TV Channels", index=False)
        worksheet = writer.sheets["YouTube TV Channels"]
        worksheet.freeze_panes(1, 0)

    print(f"Excel file saved successfully: {output_file}")

except Exception as e:
    print(f"Error: {e}")

finally:
    driver.quit()
