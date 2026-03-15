import json
import os
import sys
import shutil

def get_data_dir():
    """Get the user data directory for the app"""
    if os.name == 'nt':  # Windows
        data_dir = os.path.join(os.environ['APPDATA'], 'QurbaniManagementSystem')
    else:  # Linux/Mac
        data_dir = os.path.join(os.path.expanduser('~'), '.qurbani_management')
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.dirname(__file__))  # Go up to project root
    return os.path.join(base_path, relative_path)

DATA_DIR = get_data_dir()
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")

# Copy config from bundle if frozen and not exists
if getattr(sys, 'frozen', False) and not os.path.exists(CONFIG_FILE):
    bundle_config = os.path.join(sys._MEIPASS, "config.json")
    if os.path.exists(bundle_config):
        shutil.copy(bundle_config, CONFIG_FILE)

DEFAULT_CONFIG = {
    "language": "en",
    "receipt_bg_path": None,
    "mosque_name": "Ijtimai Qurbani Center"
}

class ConfigManager:
    @staticmethod
    def load_config():
        if not os.path.exists(CONFIG_FILE):
            ConfigManager.save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            return DEFAULT_CONFIG

    @staticmethod
    def save_config(config):
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)

    @staticmethod
    def get(key, default=None):
        config = ConfigManager.load_config()
        return config.get(key, default)

    @staticmethod
    def set(key, value):
        config = ConfigManager.load_config()
        config[key] = value
        ConfigManager.save_config(config)