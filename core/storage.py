import json
import os

DATA_DIR = "bot_data"
LEVELS_FILE = f"{DATA_DIR}/levels.json"
TICKETS_FILE = f"{DATA_DIR}/tickets.json"

os.makedirs(DATA_DIR, exist_ok=True)

def load_json(path, default):
    if not os.path.exists(path):
        save_json(path, default)
        return default
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

levels_data = load_json(LEVELS_FILE, {})
tickets_data = load_json(TICKETS_FILE, {})