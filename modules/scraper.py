import json
import re
import sys
from datetime import datetime
from getpass import getpass
import requests
from requests.exceptions import RequestException
from modules.argument_manager import ArgumentManager
from modules.errors import AuthenticationFailException
from modules.file_utils import get_data_from_local, save_metrics
from modules.session_utils import load_cookies, save_cookies

BASE_URL = "https://www.instagram.com"
FOLLOWERS_URL = BASE_URL + "/{}/followers/"
FOLLOWING_URL = BASE_URL + "/{}/following/"
LOGIN_URL = BASE_URL + "/accounts/login/ajax/"
SECURITY_LOGIN_URL = LOGIN_URL + "two_factor/"
USER_QUERY = BASE_URL + "/web/search/topsearch/?query={}"
GRAPHQL_QUERY = BASE_URL + "/graphql/query/?query_hash={}&variables={}"
FOLLOWERS_QUERY_HASH = "c76146de99bb02f6415203be841dd25a"
FOLLOWINGS_QUERY_HASH = "d04b0a864b4b54837c0d870b0e77e076"
TIME_LIMIT = "🚫 Execution interrupted. For safety reasons, you must wait 60 minutes before retrieving the data again"

class Scraper():

    def __init__(self, arguments:ArgumentManager=None):
        print("🚀 The environment is getting ready...")

        self.session = requests.session()
        self.args = arguments
        self._user = None
        self._user_id = None
        self._password = None
        self._payload = {}
        self._auth_cookies = {}
        self._auth_headers = {}
        self._followers = []
        self._followings = []

        load_cookies(self.session)

    def close(self):
        self.session.close()

    def authenticate(self):
        try:
            if self._login_required():
                print("🔐 Account credentials is required")
                self._login()

            if not self._user:
                self._get_user()
            if not self._user_id:
                self._get_user_id()
        except AuthenticationFailException as e:
            self._show_error_and_exit(str(e))

    def _login_required(self):
        print("🔐 Checking login status...")
        return self.session.cookies.get("csrftoken") is None

    def _login(self):
        self._ask_credentials()
        self._get_login_headers()
        if self._auth_headers:
            self._login_execute()
            return
        raise AuthenticationFailException("Failed to get login headers")

    def _ask_credentials(self):
        username = input("🔑 Enter username: ")
        print("🔑 ", end="", flush=True)
        password = getpass("Enter password: ")

        self._user = username
        self._password = password

    def _get_login_headers(self):
        try:
            response = self.session.get(LOGIN_URL, timeout=10)
        except RequestException as req_exception:
            print(f"GET RequestException: {req_exception}")
            return
        else:
            self._save_auth_headers(response.cookies.get_dict(".instagram.com"))      

    def _save_auth_headers(self, cookies):
        csrf = cookies["csrftoken"]
        mid = cookies["mid"]
        ig_did = cookies["ig_did"]
        ig_nrcb = cookies["ig_nrcb"]
        headers = {
            'X-CSRFToken': f'{csrf}',
            'Cookie': f"csrftoken={csrf}; mid={mid}; ig_did={ig_did}; ig_nrcb={ig_nrcb};"
        }
        self._auth_headers = headers

    def _login_execute(self):
        int_time = int(datetime.now().timestamp())
        payload = {
            'username': self._user,
            'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{int_time}:{self._password}',
            'queryParams': {},
            'optIntoOneTap': 'true' 
        }
        self._attempt_login(LOGIN_URL, payload)

    def _attempt_login(self, url, payload):
        headers = self._auth_headers
        response = self.session.post(url, data=payload, headers=headers, timeout=10)

        try:
            data = response.json()
            self._parse_login(data)
        except (json.decoder.JSONDecodeError, AttributeError):
            raise AuthenticationFailException("Unexpected login response")

    def _parse_login(self, data):
        if data:
            if data.get("authenticated"):
                print("🔓 Successful login")
                save_cookies(self.session)
                return
            if data.get("two_factor_required") and data.get("two_factor_info"):
                print("🔐 Two factor authentication is required")
                self._login_two_factor(data.get("two_factor_info").get("two_factor_identifier"))
                return
        raise AuthenticationFailException("Login unsuccessful")

    def _login_two_factor(self, identifier):
        security_code = input("🔑 Enter the security code: ")
        payload = {
            "username": self._user,
            "verificationCode": security_code,
            "identifier": identifier
        }
        
        self._attempt_login(SECURITY_LOGIN_URL, payload)

    def _get_user(self):
        response = self.session.get(BASE_URL, timeout=10)
        username_match = re.search('"username":"(.*?)","is_supervised', str(response.content))
        if username_match:
            print("🔓 Successful login")
            self._user = username_match.group(1)
            return
        raise AuthenticationFailException("Could not retrieve your username from session")

    def _get_user_id(self):
        response = self.session.get(USER_QUERY.format(self._user), timeout=10)
        try:
            data = response.json()
            self._user_id = data['users'][0]['user']['pk']
        except (json.decoder.JSONDecodeError, AttributeError):
            raise AuthenticationFailException("Unexpected user_id response")

    def get_groups(self):
        self._check_time_restriction()
        print("⏳ Getting followers/followings, this may take a while...")
        followers = self._get_group("followers")
        followings = self._get_group("followings")

        self._followers = followers
        self._followings = followings

    def _check_time_restriction(self):
        metrics = get_data_from_local(self._user)
        if metrics:
            last_update = metrics[0]['last_update']
            date_format = "%Y-%m-%d %H:%M:%S.%f"
            last_update = datetime.strptime(last_update, date_format)
            diff = (datetime.now() - last_update).total_seconds() / 60

            if not diff >= 60:
                print(TIME_LIMIT)
                print(f"🕒 Last update was on {last_update.strftime('%Y-%m-%d %H:%M')}")
                sys.exit()

    def _get_group(self, group_name):
        """Retrieves the list of the group given."""
        is_followers = group_name == "followers"
        group_query_hash = FOLLOWERS_QUERY_HASH if is_followers else FOLLOWINGS_QUERY_HASH
        edge_type = 'edge_followed_by' if is_followers else 'edge_follow'
        data = []
        after = None
        has_next = True

        while has_next:
            variables = {
                "id": self._user_id,
                "include_reel": False,
                "fetch_mutual": False,
                "first": 50,
                "after": after
            }

            try:
                response = self.session.get(GRAPHQL_QUERY.format(group_query_hash,json.dumps(variables)), timeout=10)
            except RequestException as e:
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
        print("📊 Almost done! Doing some maths...")

        followings = self._followings
        followers = self._followers
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
        data_to_save = []
        metrics = {
            "followings": followings,
            "followers": followers,
            "dont_follow_me_back": dont_follow_me_back,
            "dont_follow_back": dont_follow_back
        }
        data_to_save.append({"metrics": metrics, "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")})
        save_metrics(self._user, data_to_save)

    def _show_error_and_exit(self, message):
        print(f"😵 Oops! An error has occurred and the execution has been cancelled\n{message}")
        self.close()
        sys.exit()
