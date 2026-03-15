import json
import os

CONFIG_FILE = "config.json"
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