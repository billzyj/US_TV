import os
import re
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.WebDriverUtils import run_webdriver, OUTPUT_DIR

# VARIABLES FOR FLEXIBILITY
YOUTUBE_TV_URL = "https://tv.youtube.com/welcome/?utm_servlet=prod&rd_rsn=asi&zipcode=79423"
ZIPCODE = "79423"
MODAL_SELECTOR = "tv-network-browser-matrix"
CONTENT_DIV_CLASS = "tv-network-matrix__body"
COMPARE_BUTTON_CLASS = "tv-network-browser__input-area-submit"

def scrape_youtube_tv():
    driver = run_webdriver()
    driver.get(YOUTUBE_TV_URL)
    
    try:
        print("WAITING FOR PAGE TO LOAD...")
        time.sleep(5)  # ALLOW JAVASCRIPT EXECUTION

        # LOCATE AND CLICK THE COMPARE PLANS BUTTON
        print("LOCATING COMPARE PLANS BUTTON...")
        compare_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CLASS_NAME, COMPARE_BUTTON_CLASS))
        )
        driver.execute_script("arguments[0].click();", compare_button)  # SIMULATE USER CLICK
        print("COMPARE PLANS WINDOW OPENED SUCCESSFULLY.")

        # WAIT FOR CHANNEL LIST TO LOAD IN MODAL
        print("WAITING FOR CHANNEL LIST TO LOAD...")
        WebDriverWait(driver, 30).until(
            lambda d: d.execute_script(f"""
                let modal = document.querySelector('{MODAL_SELECTOR}');
                return modal && modal.innerText.trim().length > 0;
            """)
        )
        print("CHANNEL LIST LOADED SUCCESSFULLY.")

        # EXTRACT CHANNEL CONTENT USING JAVASCRIPT
        modal_content = driver.execute_script(f"""
            let modal = document.querySelector('{MODAL_SELECTOR}');
            return modal ? modal.innerHTML : 'Not Found';
        """)
        
        # IF CONTENT IS NOT FOUND, EXIT SCRIPT
        if modal_content == "Not Found" or modal_content.strip() == "":
            print("ERROR: CHANNEL LIST NOT FOUND.")
            driver.quit()
            exit()

        # EXTRACT CHANNEL NAMES FROM INNER HTML
        channel_names = re.findall(r'Button - (.*?) \(all-channels\)', modal_content)
        print(f"EXTRACTED {len(channel_names)} CHANNELS FROM YOUTUBE TV.")

        # CONVERT DATA TO DATAFRAME
        df_youtube_tv = pd.DataFrame(channel_names, columns=["Channel Name"])

        # SAVE TO EXCEL WITH FORMATTING
        with pd.ExcelWriter(OUTPUT_FILE, engine="xlsxwriter") as writer:
            df_youtube_tv.to_excel(writer, sheet_name="YouTube TV Channels", index=False)
            worksheet = writer.sheets["YouTube TV Channels"]
            worksheet.freeze_panes(1, 0)  # FREEZE THE FIRST ROW

        print(f"EXCEL FILE SAVED SUCCESSFULLY: {OUTPUT_FILE}")

    except Exception as e:
        print(f"ERROR: {e}")

    finally:
        driver.quit()
