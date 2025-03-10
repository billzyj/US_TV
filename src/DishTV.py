import os
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.WebDriverUtils import ZIPCODE, OUTPUT_DIR, LOGGER, load_page,  extract_channel_data, set_zipcode, write_to_excel

# Variables for flexibility
DISH_URL = "https://www.dish.com/"
PLANS_UL_ID = "navList_TV Packages"
PLAN_LI_ID = "navLink_shop"
ZIP_INPUT_ARIA_LABEL = "Results for"
ZIP_INPUT_CLASS = "cmp-textinput__input"
CHANNELS_DIV_CLASS = "cmp-singlepackageclu__channellist"
CHANNEL_CLASS = "cmp-singlepackageclu__channel"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "DishTVChannelList.xlsx")

def scrape_dishtv(mode="headless"):
    """Scrapes live channel data from DishTV."""
    driver = load_page(mode, "DishTV", DISH_URL)
    channels, plans = {}, {}
    try:
        all_channels = {}  # Dictionary to store channels across plans

        # Get plans name and url in the list
        LOGGER.info("Locating plans info...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, PLANS_UL_ID))
        )

        # Extract plan names & URLs
        plan_elements = driver.find_elements(By.XPATH, f"//ul[contains(@id, '{PLANS_UL_ID}')]//a")
        plans = {}
        for pkg in plan_elements:
            plan_name = pkg.get_attribute("aria-label")  # First try aria-label (reliable)
            if not plan_name:
                plan_name = pkg.text.strip()  # Fallback to .text if aria-label is missing
            
            plan_url = pkg.get_attribute("href")
            
            if plan_name:  # Ensure we don't store empty keys
                plans[plan_name] = plan_url
        LOGGER.info(f"Found {len(plans)} plans:", plans)

        # Iterate over each plan to scrape channels
        for plan_name, plan_url in plans.items():
            LOGGER.info(f"Processing plan: {plan_name}...")
            driver.get(plan_url)  # Navigate to plan page

            # Set ZIP code and mimic "Enter" key press
            zip_input_box = set_zipcode(driver, ZIPCODE, (By.XPATH, f"//input[@aria-label='{ZIP_INPUT_ARIA_LABEL}']"))
            zip_input_box.send_keys(Keys.ENTER)  # Simulate pressing Enter
            time.sleep(1)  # Ensure the page fully loads

            channels = extract_channel_data(driver, (By.CLASS_NAME, CHANNELS_DIV_CLASS), (By.CLASS_NAME, CHANNEL_CLASS))
            LOGGER.info(f"Extracted {len(channels)} channels for {plan_name}.")

            for channel in channels:
                try:
                    channel_name = channel.find_element(By.TAG_NAME, "p").text.strip()
                    # Extract only the name after "-"
                    channel_name = channel_name.split(" - ")[-1] if " - " in channel_name else channel_name

                    # Store channel in dictionary (mark available in this plan)
                    if channel_name not in all_channels:
                        all_channels[channel_name] = {pkg: "" for pkg in plans.keys()}  # Initialize row
                    all_channels[channel_name][plan_name] = "✔️"  # Mark availability
                except Exception as e:
                    LOGGER.info(f"Error extracting channel name: {e}")

        # Convert dictionary to DataFrame
        df_dishtv = pd.DataFrame.from_dict(all_channels, orient="index")
        df_dishtv.index.name = "Channel Name"

        # Save to Excel with a frozen first row and filtering enabled
        write_to_excel(df_dishtv, OUTPUT_FILE, sheet_name="DishTV Channels", index=True)

    except Exception as e:
        LOGGER.error(f"Error: {e}")

    finally:
        driver.quit()
        return all_channels, plans.keys()