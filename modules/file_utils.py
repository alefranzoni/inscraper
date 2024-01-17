"""
This module is responsible for handling the local files.
"""
import os
import pickle

REPORTS_PATH = 'reports/{}/data.pkl'

def save_metrics(username, data):
    """Saves the scraped data and its metrics into a file."""
    os.makedirs(os.path.dirname(REPORTS_PATH.format(username)), exist_ok=True)
    with open(REPORTS_PATH.format(username), 'wb') as f:
        pickle.dump(data, f)

def get_metrics(username):
    """Retrieves the latest metrics obtained from the user data file."""
    if data_file_exists(username):
        with open(REPORTS_PATH.format(username), 'rb') as f:
            return pickle.load(f)
    return None

def data_file_exists(username):
    """Checks if the pkl file exists for given user."""
    return os.path.exists(REPORTS_PATH.format(username))
