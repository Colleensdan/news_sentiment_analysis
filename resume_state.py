import json
import os

RESUME_STATE_FILE = "resume_state.json"

def load_resume_state():
    """
    Load a dictionary mapping keywords to the next page number from the JSON file.
    If the file doesn't exist, return an empty dictionary.
    """
    if os.path.exists(RESUME_STATE_FILE):
        with open(RESUME_STATE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_resume_state(state):
    """
    Save the given dictionary (mapping keywords to the next page) into the JSON file.
    """
    with open(RESUME_STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)
