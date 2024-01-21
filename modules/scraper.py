"""
This module contains the implementation of a scraper for Instagram based on Playwright.
The scraper is designed to login and get the followers/following list from a specific user given.
"""
import json
import re
import sys
import time
from datetime import datetime
import requests
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from modules.argument_manager import ArgumentManager
from modules.file_utils import get_data_from_local, save_metrics
from modules.session_utils import add_cookies, get_cookies, save_cookies

BASE_URL = "https://www.instagram.com/"
FOLLOWERS_URL = BASE_URL + "{}/followers/"
FOLLOWING_URL = BASE_URL + "{}/following/"
USER_QUERY = BASE_URL + "web/search/topsearch/?query={}"
GRAPHQL_QUERY = BASE_URL + "graphql/query/?query_hash={}&variables={}"
FOLLOWERS_QUERY_HASH = "c76146de99bb02f6415203be841dd25a"
FOLLOWINGS_QUERY_HASH = "d04b0a864b4b54837c0d870b0e77e076"
FAILED_LOGIN = "🧐 Oops! Looks like something went wrong. Check your credentials or connection and try again later"
FORBIDDEN_EXECUTION = "🚫 Execution interrupted! For safety reasons, you must wait 60 minutes before retrieving the data again"

class Scraper():
    """
    Playwright based Instagram scraper. 
    It's able to start up a browser, authenticate to Instagram and get the followers/following 
    list from a specific user given.
    """

    def __init__(self, headless=True, arguments:ArgumentManager=None):
        """Initialize the Scraper object."""
        print("🚀 The environment is getting ready...")
        self.headless = headless
        self.args = arguments
        self.browser = sync_playwright().start()

    def close(self):
        """Close the browser."""
        self.browser.close()

    def authenticate(self, username, password):
        """Authenticate to Instagram with the provided credentials."""
        print("🌎 Navigating and loading Instagram page")
        self.target = username
        self.browser = self.browser.firefox.launch(headless=self.headless)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        add_cookies(context=self.context)
        self._navigate(BASE_URL)
        print("🛡️  Starting the authentication process")
        login_selector = self.page.query_selector('button[type="submit"]')
        if login_selector:
            self._login(username, password, login_selector)
            if self._check_protection_auth():
                self._two_factor_resolver()
            save_cookies(context=self.context)
        self._check_login_state()

    def _login(self, username, password, login_selector):
        """Performs the login with the credentials given.""" 
        self.page.fill('input[name="username"]', username)
        self.page.fill('input[name="password"]', password)
        login_selector.click()
        time.sleep(2)
        wrong_password = re.search("Sorry, your password was incorrect", self.page.content())
        if wrong_password:
            print(FAILED_LOGIN)
            self.close()
            sys.exit()

    def _two_factor_resolver(self):
        """Resolves the two factor auth logic to login."""
        print("🔐 Two factor authentication is required")
        auth_code = input("🔑 Enter the 2FA code: ")
        self.page.fill('input[name="verificationCode"]', auth_code)
        self.page.click('button[type="button"]')
        time.sleep(4)

    def _check_login_state(self):
        """Checks if the user is logged in."""
        print("🔒 Checking login status")
        self._navigate(BASE_URL + self.target)
        logout_token = re.search("logoutToken", self.page.content())
        if logout_token:
            print("🔓 Successful login")
        else:
            print(FAILED_LOGIN)
            self.close()
            sys.exit()

    def _navigate(self, url):
        """Navigates to specified url."""
        self.page.goto(url, wait_until="networkidle")

    def get_groups(self):
        """Gets the list of followers/followings and calculate the metrics."""
        if not self._check_time_restriction():
            print(FORBIDDEN_EXECUTION)
            print(f"🕒 Last update was on {self.last_update.strftime('%Y-%m-%d %H:%M')}")
            return
        print("⏳ Getting followers/followings, this may take a while...")
        cookies_list = get_cookies()
        cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies_list}
        user_id = self._get_user_id(cookies_dict)
        followers = self._get_group(user_id, "followers", cookies_dict)
        followings = self._get_group(user_id, "followings", cookies_dict)
        print("📊 Almost done! Doing some maths...")
        dont_follow_me_back = [following for following in followings if not any(follower['username'] == following['username'] for follower in followers)]
        dont_follow_back = [follower for follower in followers if not any(following['username'] == follower['username'] for following in followings)]
        if len(dont_follow_me_back) == 0:
            print("🤩 Congratulations, everyone follows you!")
        else:
            print("🔎 Users who don't follow you back")
            for index, user in enumerate(dont_follow_me_back):
                print(f"   {index + 1}. {user['full_name']} ({user['username']})")
        data_to_save = []
        metrics = {
            "followings": followings,
            "followers": followers,
            "dont_follow_me_back": dont_follow_me_back,
            "dont_follow_back": dont_follow_back
        }
        data_to_save.append({"metrics": metrics, "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")})
        save_metrics(self.target, data_to_save)

    def _check_time_restriction(self):
        """Checks if the required time (1 hour) has elapsed since the last data was collected."""
        metrics = get_data_from_local(self.target)
        if metrics:
            last_update = metrics[0]['last_update']
            date_format = "%Y-%m-%d %H:%M:%S.%f"
            last_update = datetime.strptime(last_update, date_format)
            diff = (datetime.now() - last_update).total_seconds() / 60
            self.last_update = last_update
            return diff >= 60
        return True

    def _get_user_id(self, cookies):
        """Gets the user id needed to do the requests."""
        user_query = requests.get(USER_QUERY.format(self.target), cookies=cookies)
        user_query_json = user_query.json()
        return user_query_json['users'][0]['user']['pk']

    def _get_group(self, user_id, group_name, cookies):
        """Retrieves the list of the group given."""
        is_followers = group_name == "followers"
        group_query_hash = FOLLOWERS_QUERY_HASH if is_followers else FOLLOWINGS_QUERY_HASH
        edge_type = 'edge_followed_by' if is_followers else 'edge_follow'
        data = []
        after = None
        has_next = True
        while has_next:
            variables = {
                "id": user_id,
                "include_reel": False,
                "fetch_mutual": False,
                "first": 50,
                "after": after
            }
            response = requests.get(GRAPHQL_QUERY.format(group_query_hash, json.dumps(variables)), cookies=cookies)
            response_json = response.json()
            has_next = response_json['data']['user'][edge_type]['page_info']['has_next_page']
            after = response_json['data']['user'][edge_type]['page_info']['end_cursor']
            edges = response_json['data']['user'][edge_type]['edges']
            for edge in edges:
                node = edge['node']
                data.append({
                    "username": node['username'],
                    "full_name": node['full_name']
                })
        print(f"👥 {group_name.capitalize()} fetched successfully ({len(data)})")
        return data

    def _check_protection_auth(self):
        """Check if two factor authentication is required."""
        try:
            self.page.wait_for_function('() => window.location.href.includes("login/two_factor")', timeout=3000)
            return True
        except PlaywrightTimeoutError:
            return False
