import unittest
from src.WebDriverUtils import run_webdriver, setup_logger

class TestWebDriverUtils(unittest.TestCase):
    def test_run_webdriver_headless(self):
        """Test that run_webdriver initializes in headless mode."""
        driver = run_webdriver("headless")
        self.assertIsNotNone(driver)
        driver.quit()

    def test_run_webdriver_gui(self):
        """Test that run_webdriver initializes in GUI mode."""
        driver = run_webdriver("gui")
        self.assertIsNotNone(driver)
        driver.quit()

    def test_setup_logger(self):
        """Test that setup_logger returns a logger with the correct level."""
        logger = setup_logger()
        self.assertEqual(logger.level, 10)  # DEBUG level

if __name__ == "__main__":
    unittest.main() 