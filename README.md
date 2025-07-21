# US TV Channel Web Scraping Project

## TODO
- [x] Test headless mode
- [x] Improve error handling for provider site changes
- [x] Optimize Selenium scraping speed
- [x] Add support for additional streaming services
- [x] Implement a GUI for non-technical users
- [x] Add individual scraper runs for debugging
- [x] Improve error handling and partial results

## Overview

This project is a **TV channel lineup scraper** that collects live channel data from various TV service providers, including **DirecTV, DirecTV Stream, DishTV, FuboTV, HuluTV, SlingTV, and YouTubeTV**. It automates data extraction from provider websites and consolidates it into a structured **Excel report** for easy comparison.

## Features

- **Automated Web Scraping**: Uses Selenium to extract TV channel lineups
- **Supports Multiple Providers**: Scrapes data from major TV providers
- **ZIP Code Customization**: Configurable ZIP code input for localized channel availability
- **Consolidated Report**: Aggregates channel listings across providers into an Excel file
- **Filtering & Sorting**: Generates a formatted, sortable Excel sheet with channel availability across plans
- **Individual Scraper Runs**: Run specific scrapers for debugging or partial updates
- **Graceful Error Handling**: Continues processing even if some scrapers fail
- **User-Friendly GUI**: Easy-to-use interface for non-technical users

## Installation

### Prerequisites

Ensure you have the following installed:

- **Python 3.x**
- **Google Chrome**
- **Chromedriver** (managed automatically by `webdriver_manager`)
- Required Python libraries:
  ```sh
  pip install -r requirements.txt
  ```

### Environment Setup

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/US_TV.git
   cd US_TV
   ```

2. Set up a virtual environment (optional but recommended):
   ```sh
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   ```

3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

4. Configure the project:
   - Edit `config.json` to set your ZIP code and output directory

## Usage

### Command Line Interface

Run the scraper with various options:

```sh
# Run all scrapers in headless mode (default)
python TV_Webscraping.py

# Run specific providers
python TV_Webscraping.py --providers sling directv

# Run in GUI mode
python TV_Webscraping.py --mode gui

# Output as CSV instead of Excel
python TV_Webscraping.py --output csv
```

Available options:
- `--mode`: Choose between 'headless' (default) or 'gui' mode
- `--output`: Select output format ('excel' or 'csv')
- `--providers`: Specify which providers to scrape (e.g., 'sling', 'directv', 'dish', etc.)

### Using the GUI

For a user-friendly interface, run the GUI:

```sh
python src/GUI.py
```

The GUI provides:
- Provider selection via checkboxes
- WebDriver mode selection (headless/GUI)
- Output format selection (Excel/CSV)
- Progress indication
- Success/error notifications

### Output Format

The final Excel/CSV file `Summary_TV_Channels.xlsx` contains:

- **Channel Name**: Unified listing of TV channels
- **Channel Numbers**: DirecTV & DirecTV Stream numbers
- **Plan Availability**: Columns for each provider's plans with checkmarks (✔️) for availability

## Debugging

### Individual Scraper Runs

To debug a specific provider:

```sh
# Run only SlingTV scraper
python TV_Webscraping.py --providers sling

# Run multiple specific scrapers
python TV_Webscraping.py --providers directv dish
```

### Error Handling

- Failed scrapers are logged but don't prevent other scrapers from running
- Partial results are still generated even if some scrapers fail
- Detailed error messages are shown in the GUI and logs

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
│   ├── GUI.py                    # User interface for the scraper
├── output/                       # Directory where Excel files are saved
├── data/                         # Channel alias mappings
```

## Troubleshooting

- **Missing Channels?** Websites may have changed their structure. Inspect elements and update the scraping logic accordingly.
- **WebDriver Errors?** Ensure your Chrome browser and Chromedriver are up to date.
- **Timeout Errors?** Increase WebDriver wait times in `WebDriverUtils.py`.
- **Logging Issues?** Check the `output` directory for log files and ensure logging is configured correctly.
- **Individual Scraper Failing?** Run it separately using the `--providers` option to debug.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the **MIT License**, which can be found in the root folder.

