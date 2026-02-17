import json
import os

DATA_DIR = "bot_data"
CONFIG_FILE = f"{DATA_DIR}/config.json"

DEFAULT_CONFIG = {
    "xp_per_message_min": 50,
    "xp_per_message_max": 95,
    "xp_per_voice_minute": 0.5,
    "xp_cooldown_ms": 1400,
    "level_curve": "easy_linear",
    "level_up_channel": None,
    "level_up_mode": "only-role-rewards",
    "blacklisted_channels": [],
    "blacklisted_roles": [],
    "level_rewards": {
        "1": "Economy",
        "3": "Premium economy",
        "5": "Business class",
        "10": "First Class"
    },
    "xp_multiplier_roles": {},
    "xp_multiplier_channels": {
        "chatroom": 2
    },
    "only_keep_highest_role": True,
    "reset_level_on_leave": False,
    "welcome_channel": None,
    "ticket_category": None,
    "ticket_log_channel": None
}

os.makedirs(DATA_DIR, exist_ok=True)

def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

config = load_config()