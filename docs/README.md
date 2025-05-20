# TV Channel Web Scraper Documentation

## Setup

1. **Prerequisites:**
   - Python 3.x
   - Google Chrome
   - Required Python libraries (install via `pip install -r requirements.txt`)

2. **Environment Setup:**
   - Clone the repository:
     ```sh
     git clone https://github.com/yourusername/US_TV.git
     cd US_TV
     ```
   - Set up a virtual environment (optional but recommended):
     ```sh
     python -m venv venv
     source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
     ```
   - Install dependencies:
     ```sh
     pip install -r requirements.txt
     ```
   - Configure the project:
     - Edit `config.json` to set your ZIP code and output directory.

## Running the Scraper

### Command Line

Run the scraper using the command line:

```sh
python TV_Webscraping.py --mode headless  # (default, runs browser in background)
python TV_Webscraping.py --mode gui       # (shows browser window for debugging)
```

### GUI

For a user-friendly interface, run the GUI:

```sh
python src/GUI.py
```

This will open a window where you can select the WebDriver mode (headless or GUI) and run the scraper with a single click.

## Testing

Run the unit tests using:

```sh
python -m unittest discover tests
```

### Adding New Tests

To add new tests, create a new test file in the `tests` directory. Follow the existing test structure and ensure all tests are passing before submitting a pull request.

## CI/CD

The project uses GitHub Actions for continuous integration. Tests are automatically run on every push and pull request to the `main` branch.

### Setting Up CI/CD Locally

1. Install GitHub Actions CLI tools.
2. Configure your local environment to match the CI environment.
3. Run the CI workflow locally to ensure everything is set up correctly.

## Logging

Logs are stored in the `output` directory. The log file is rotated to prevent it from growing too large.

### Logging Configuration

- Logs are written to `tv_scraper.log`.
- Log rotation is configured to keep the last 5 log files, each with a maximum size of 10MB.

## FAQ

- **Q: How do I update the ZIP code?**
  - A: Edit the `ZIPCODE` in `config.json`.

- **Q: What should I do if the scraper fails to load a page?**
  - A: Check the log files for errors and ensure your internet connection is stable.

- **Q: How can I contribute to the project?**
  - A: Fork the repository, make your changes, and submit a pull request.

## Troubleshooting

- **Missing Channels?** Websites may have changed their structure. Inspect elements and update the scraping logic accordingly.
- **WebDriver Errors?** Ensure your Chrome browser and Chromedriver are up to date.
- **Timeout Errors?** Increase WebDriver wait times in `WebDriverUtils.py`. 