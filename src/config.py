import json
import os

# Default configuration
DEFAULT_CONFIG = {
    "ZIPCODE": "79423",
    "OUTPUT_DIR": "./output/"
}

CONFIG_FILE = "config.json"

def load_config():
    """Load configuration from config.json, or use defaults if file doesn't exist."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return DEFAULT_CONFIG

def save_config(config):
    """Save configuration to config.json."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4) 