# resume_state.py
import json
import os

RESUME_STATE_FILE = "resume_state.json"

def load_resume_state():
    if os.path.exists(RESUME_STATE_FILE):
        with open(RESUME_STATE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_resume_state(state):
    with open(RESUME_STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)
