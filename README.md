# US TV Channel Web Scraping Project

## TODO
- Merge similar channel names
- Test headless mode
- Improve error handling for provider site changes
- Optimize Selenium scraping speed
- Add support for additional streaming services
- Implement a GUI for non-technical users

## Overview

This project is a **TV channel lineup scraper** that collects live channel data from various TV service providers, including **DirecTV, DirecTV Stream, DishTV, FuboTV, HuluTV, SlingTV, and YouTubeTV**. It automates data extraction from provider websites and consolidates it into a structured **Excel report** for easy comparison.

## Features

- **Automated Web Scraping**: Uses Selenium to extract TV channel lineups.
- **Supports Multiple Providers**: Scrapes data from major TV providers.
- **ZIP Code Customization**: Configurable ZIP code input for localized channel availability.
- **Consolidated Report**: Aggregates channel listings across providers into an Excel file.
- **Filtering & Sorting**: Generates a formatted, sortable Excel sheet with channel availability across plans.

## Installation

### Prerequisites

Ensure you have the following installed:

- **Python 3.x**
- **Google Chrome**
- **Chromedriver** (managed automatically by `webdriver_manager`)
- Required Python libraries:
  ```sh
  pip install selenium pandas openpyxl webdriver-manager
  ```

## How It Works

1. **Scraping Functions**: Each provider has a separate scraping function that extracts channel information and saves it as a dictionary or list.
2. **Data Aggregation**: The extracted data is processed and compiled into a structured format.
3. **Excel Export**: A summary Excel file is generated with filtering and sorting enabled.

## Project Structure

```
├── src/
│   ├── WebDriverUtils.py         # Utilities for Selenium WebDriver
│   ├── TV_Webscraping.py         # Main script for running scrapers and generating reports
│   ├── DirecTV.py                # Scraper for DirecTV
│   ├── DirecTV_Stream.py         # Scraper for DirecTV Stream
│   ├── DishTV.py                 # Scraper for DishTV
│   ├── FuboTV.py                 # Scraper for FuboTV
│   ├── HuluTV.py                 # Scraper for HuluTV
│   ├── SlingTV.py                # Scraper for SlingTV
│   ├── YoutubeTV.py              # Scraper for YouTubeTV
├── output/                       # Directory where Excel files are saved
```

## Usage

### Running the Scraper

Execute the main script to scrape data and generate a consolidated report:

```sh
python TV_Webscraping.py
```

This will:

- Scrape channel data from all providers.
- Normalize and consolidate channel names.
- Generate an **Excel file** with all the data.

### Output Format

The final Excel file `Summary_TV_Channels.xlsx` contains:

- **Channel Name**: Unified listing of TV channels.
- **Channel Numbers**: DirecTV & DirecTV Stream numbers.
- **Plan Availability**: Columns for each provider's plans with checkmarks (`✔`) for availability.

## Customization

- Modify `ZIPCODE` in `WebDriverUtils.py` to scrape based on a different location.
- Adjust **plan names and provider URLs** in individual scraper scripts.
- Use the `headless` or `gui` mode when initializing Selenium WebDriver.

## Troubleshooting

- **Missing Channels?** Websites may have changed their structure. Inspect elements and update the scraping logic accordingly.
- **WebDriver Errors?** Ensure your Chrome browser and Chromedriver are up to date.
- **Timeout Errors?** Increase WebDriver wait times in `WebDriverUtils.py`.

## License

This project is licensed under the **MIT License**, which can be found in the root folder.

