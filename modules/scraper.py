"""
This module contains the implementation of a scraper for Instagram based on Playwright.
The scraper is designed to login and get the followers/following list from a specific user given.
"""
import json
import re
import sys
import time
import requests
from requests.exceptions import RequestException, ConnectionError, HTTPError, Timeout, TooManyRedirects
from datetime import datetime
from getpass import getpass
from requests.exceptions import Timeout as RequestTimeout
from modules.argument_manager import ArgumentManager
from modules.file_utils import get_data_from_local, save_metrics
from modules.session_utils import add_cookies, get_cookies, save_cookies

BASE_URL = "https://www.instagram.com/"
FOLLOWERS_URL = BASE_URL + "{}/followers/"
FOLLOWING_URL = BASE_URL + "{}/following/"
AJAX_LOGIN_URL = BASE_URL + "accounts/login/ajax/"
USER_QUERY = BASE_URL + "web/search/topsearch/?query={}"
GRAPHQL_QUERY = BASE_URL + "graphql/query/?query_hash={}&variables={}"
FOLLOWERS_QUERY_HASH = "c76146de99bb02f6415203be841dd25a"
FOLLOWINGS_QUERY_HASH = "d04b0a864b4b54837c0d870b0e77e076"
FAILED_LOGIN = "Check your credentials or connection and try again later"
FAILED_SECURITY_CODE = "Check the security code and try again"
FORBIDDEN_EXECUTION = "🚫 Execution interrupted. For safety reasons, you must wait 60 minutes before retrieving the data again"

class Scraper():
    """
    Playwright based Instagram scraper. 
    It's able to start up a browser, authenticate to Instagram and get the followers/following 
    list from a specific user given.
    """

    def __init__(self, arguments:ArgumentManager=None):
        """Initialize the Scraper object."""
        print("🚀 The environment is getting ready...")

        self.args = arguments
        self.target = None
        self.followers = None
        self.followings = None
        self.two_factor_required = None
        self.session = requests.session()

        # FIXME: Al tener ya la data de los cookies, colocarsela a la sesion
        # add_cookies(context=self.context)
        # cookies_list = get_cookies()
        # cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies_list}
        # self.session.cookies.update(cookies_dict)

    def close(self):
        """Close the browser."""
        self.session.close()

    def authenticate(self):
        """Authenticate on Instagram by logging into your account."""
        if self._login_required():
            self._login()

        self._check_success_login()

    def _login_required(self):
        """
        Determines if login is required for the user on Instagram.

        This method attempts to access a page that is typically available only to users
        who are logged in. If the response contains a redirect to the login page, it is inferred
        that the user is not currently authenticated, and login is required.
        """
        print("🔐 Checking login status...")

        response = self.session.get("https://www.instagram.com/accounts/edit/", timeout=5000)
        login_required = re.search(r'instagram\.com/accounts/login/\?next', response.text)

        return login_required

    def _login(self):
        """Performs the login.""" 
        print("🔐 Account credentials is required")
        submit_login_selector = self.page.query_selector('button[type="submit"]')
        (username, password) = self._get_credentials()

        self.target = username
        self.page.fill('input[name="username"]', username)
        self.page.fill('input[name="password"]', password)

        submit_login_selector.click()
        time.sleep(2)
        (success, two_factor_required) = self._check_credentials(username, password)

        if not success:
            self._show_error_and_exit(FAILED_LOGIN)

        if two_factor_required:
            print("🔐 Two factor authentication is required")
            self._wait_two_factor_url()
            self._two_factor_resolver()

        save_cookies(context=self.context)

    def _get_credentials(self):
        """Asks for and obtains the credentials entered by the user."""
        username = input("🔑 Enter username: ")
        print("🔑 ", end="", flush=True)
        password = getpass("Enter password: ")
        return username, password

    def _check_credentials(self, username, password):
        """Checks if the credentials are valid."""
        int_time = int(datetime.now().timestamp())
        payload = {
            'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{int_time}:{password}',
            'optIntoOneTap': 'true',
            'queryParams': {},
            'username': username
        }
        headers = {}

        try:
            response = requests.request("POST", AJAX_LOGIN_URL, headers=headers, data=payload, timeout=5000)
        except RequestTimeout as e:
            self._show_error_and_exit(str(e))

        csrf=response.cookies["csrftoken"]
        mid=response.cookies["mid"]
        ig_did=response.cookies["ig_did"]
        ig_nrcb=response.cookies["ig_nrcb"]

        headers = {
            'X-CSRFToken': f'{csrf}',
            'Cookie': f"csrftoken={csrf}; mid={mid}; ig_did={ig_did}; ig_nrcb={ig_nrcb};"
        }

        try:
            response = requests.request("POST", AJAX_LOGIN_URL, headers=headers, data=payload, timeout=5000)
        except RequestTimeout as e:
            self._show_error_and_exit(str(e))

        json_response = response.json()
        two_factor_required = json_response["status"] == "fail" and json_response["error_type"] == "two_factor_required"

        if two_factor_required:
            return True, True

        return (json_response["status"] == "ok" and
                json_response["authenticated"] is not None and
                json_response["authenticated"] is True), False

    def _wait_two_factor_url(self):
        try:
            self.page.wait_for_function('() => window.location.href.includes("login/two_factor")', timeout=3000)
        except PlaywrightTimeoutError as e:
            self._show_error_and_exit(e.message)

    def _two_factor_resolver(self):
        """Resolves the two factor auth logic to login."""
        auth_code = input("🔑 Enter the security code: ")
        self.page.fill('input[name="verificationCode"]', auth_code)
        self.page.click('button[type="button"]')
        if not self._two_factor_is_valid():
            self._show_error_and_exit(FAILED_SECURITY_CODE)

    def _two_factor_is_valid(self):
        """Validate if the security code is valid."""
        try:
            self.page.wait_for_selector('p[id="twoFactorErrorAlert"]', timeout=5000)
        except PlaywrightTimeoutError:
            return True
        return False

    def _check_success_login(self):
        """Checks if the user is logged in."""
        username_match = re.search('"username":"(.*?)","is_supervised', self.page.content())
        if username_match:
            self.target = username_match.group(1)
            print("🔓 Successful login")
        else:
            self._show_error_and_exit(FAILED_LOGIN)

    def _navigate(self, url):
        """Navigates to specified url."""
        response = self.page.goto(url, wait_until="load")
        self._handle_http_status(response.status)

    def _handle_http_status(self, status):
        if 200 <= status < 300:
            pass
        elif 400 <= status < 500:
            self._show_error_and_exit(f"Client error ({status})")
        elif 500 <= status < 600:
            self._show_error_and_exit(f"Internal server error ({status})")
        else:
            self._show_error_and_exit(f"Unknown error ({status})")

    def _show_error_and_exit(self, message):
        print(f"😵 Oops! An error has occurred and the execution has been cancelled\n{message}")
        self.close()
        sys.exit()

    def get_groups(self):
        """Gets the list of followers/followings."""
        self._check_time_restriction()
        print("⏳ Getting followers/followings, this may take a while...")

        cookies_list = get_cookies()
        cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies_list}
        user_id = self._get_user_id(cookies_dict)
        followers = self._get_group(user_id, "followers", cookies_dict)
        followings = self._get_group(user_id, "followings", cookies_dict)

        self.followers = followers
        self.followings = followings

    def _check_time_restriction(self):
        """Checks if the required time (1 hour) has elapsed since the last data was collected."""
        metrics = get_data_from_local(self.target)
        if metrics:
            last_update = metrics[0]['last_update']
            date_format = "%Y-%m-%d %H:%M:%S.%f"
            last_update = datetime.strptime(last_update, date_format)
            diff = (datetime.now() - last_update).total_seconds() / 60
            
            self.last_update = last_update
           
            if not diff >= 60:
                print(FORBIDDEN_EXECUTION)
                print(f"🕒 Last update was on {self.last_update.strftime('%Y-%m-%d %H:%M')}")
                sys.exit()

    def _get_user_id(self, cookies):
        """Gets the user id needed to do the requests."""
        try:
            user_query = requests.get(USER_QUERY.format(self.target), cookies=cookies, timeout=10000)
        except RequestTimeout as e:
            self._show_error_and_exit(str(e))

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

            try:
                response = requests.get(
                    GRAPHQL_QUERY.format(group_query_hash, json.dumps(variables)),
                    cookies=cookies,
                    timeout=10000
                )
            except RequestTimeout as e:
                self._show_error_and_exit(str(e))

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

    def show_metrics(self):
        """Calculates and show the metrics based on the followers and followings list."""
        print("📊 Almost done! Doing some maths...")

        followings = self.followings
        followers = self.followers
        dont_follow_me_back = [following for following in followings if not any(follower['username'] == following['username'] for follower in followers)]
        dont_follow_back = [follower for follower in followers if not any(following['username'] == follower['username'] for following in followings)]

        if len(dont_follow_me_back) == 0:
            print("🤩 Congratulations, everyone follows you!")
        else:
            print("🔎 Users who don't follow you back")
            for index, user in enumerate(dont_follow_me_back):
                print(f"   {index + 1}. {user['full_name']} ({user['username']})")

        self._save_metrics(followers, followings, dont_follow_me_back, dont_follow_back)

    def _save_metrics(self, followers, followings, dont_follow_me_back, dont_follow_back):
        """Prepares and save the user metrics locally."""
        data_to_save = []
        metrics = {
            "followings": followings,
            "followers": followers,
            "dont_follow_me_back": dont_follow_me_back,
            "dont_follow_back": dont_follow_back
        }
        data_to_save.append({"metrics": metrics, "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")})
        save_metrics(self.target, data_to_save)
