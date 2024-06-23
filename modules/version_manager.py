import requests
from modules.utils import print_red

CURRENT = "3.0.0"
RELEASES_API = "https://api.github.com/repos/alefranzoni/inscraper/releases"
REPO_URL = "https://github.com/alefranzoni/inscraper/"

def get_latest_version():
    response = requests.get(RELEASES_API, timeout=10)
    data = response.json()
    latest_version = data[0]["tag_name"]
    return latest_version.replace("v", "")

def check_updates():
    latest_version = get_latest_version()
    if latest_version > CURRENT:
        print_red("New version is available, update the script to get the latest features")
        print_red(f"For further details visit {REPO_URL}")
