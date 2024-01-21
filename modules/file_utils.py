"""
This module is responsible for handling the local files.
"""
import os
import pickle
import sys

REPORTS_PATH = 'reports/{}/data.pkl'

def save_metrics(user, data):
    """Saves the scraped data and its metrics into a file."""
    os.makedirs(os.path.dirname(REPORTS_PATH.format(user)), exist_ok=True)
    with open(REPORTS_PATH.format(user), 'wb') as f:
        pickle.dump(data, f)

def get_data_from_local(user):
    """Retrieves the latest metrics obtained from the user data file."""
    if data_file_exists(user):
        with open(REPORTS_PATH.format(user), 'rb') as f:
            return pickle.load(f)
    return None

def data_file_exists(user):
    """Checks if the pkl file exists for given user."""
    return os.path.exists(REPORTS_PATH.format(user))

def handle_show_report(user):
    """
    Handles the report display for a given user, showing metrics about followers and followings.
    """
    if user:
        data = get_data_from_local(user)
        if data:
            metrics = data[0]['metrics']
            print(f"👥 Followings: {len(metrics['followings'])}")
            print(f"👥 Followers: {len(metrics['followers'])}")
            print("🔎 Users who don't follow you back")
            _print_enumerate_report(metrics['dont_follow_me_back'])
            print("🔎 Users who you don't follow back")
            _print_enumerate_report(metrics['dont_follow_back'])
        else:
            print(f"🧐 No previous information has been found for {user}, so, there's nothing to show")
        print("✅ Done, thanks for using Inscraper!")
        print("🌟 Star the project on GitHub", "\n- https://github.com/alefranzoni/inscraper")
        sys.exit()

def _print_enumerate_report(group):
    """Prints an enumerate list from the group given."""
    for index, user in enumerate(group):
        print(f"   {index + 1}. {user['full_name']} ({user['username']})")
