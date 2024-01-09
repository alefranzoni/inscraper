"""
This module contains the implementation of a scraper for Instagram based on Playwright.
The scraper is designed to login and get the followers/following list from a specific user given.
"""
import re
import sys
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from modules.argument_manager import ArgumentManager, ArgumentOptions
from modules.session_utils import add_cookies, save_cookies


BASE_URL = "https://www.instagram.com/"
FOLLOWERS_URL = BASE_URL + "{}/followers/"
FOLLOWING_URL = BASE_URL + "{}/following/"
FAILED_LOGIN = "🧐 Oops! Looks like something went wrong. Check your credentials or connection and try again later"

class Scraper():
    """
    Playwright based Instagram scraper. 
    It's able to start up a browser, authenticate to Instagram and get the followers/following list from a specific user given.
    """

    def __init__(self, headless=True, arguments:ArgumentManager=None):
        """Initialize the Scraper object."""
        print("🚀 The environment is getting ready...")
        self.headless = headless
        self.args = arguments
        self.scroll_retries = self._get_scroll_retries()
        self.scroll_delay = self._get_scroll_delay()
        self.browser = sync_playwright().start()

    def close(self):
        """Close the browser."""
        self.browser.close()

    def authenticate(self, username, password):
        """Authenticate to Instagram with the provided credentials."""
        print("🌎 Navigating and loading Instagram page (might take a while)")
        self.target = username
        self.browser = self.browser.firefox.launch(headless=self.headless)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        add_cookies(context=self.context)
        self._navigate(BASE_URL)
        print("🔒 Starting the authentication process")
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
        print("🔐 Checking login status")
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

    def get_users(self):
        """Get the list of followers and following users in that order."""
        groups = ["followers", "following"]
        for group in groups:
            self._open_modal(self._get_link(group))
            self._scroll_to_bottom(group)
            if group == "followers":
                followers = self._get_list()
            else:
                following = self._get_list()
        return followers, following

    def _check_protection_auth(self):
        """Check if two factor authentication is required."""
        try:
            self.page.wait_for_function('() => window.location.href.includes("login/two_factor")', timeout=3000)
            return True
        except PlaywrightTimeoutError:
            return False

    def _open_modal(self, link):
        """Open the modal with the list of followers or following users."""
        self._navigate(link)
        self.page.wait_for_selector("div[class='_aano']")

    def _get_link(self, group):
        """Get the link to the followers or following list."""
        print(f"👥 Opening {group} list")
        if group == "followers":
            return FOLLOWERS_URL.format(self.target)
        if group == "following":
            return FOLLOWING_URL.format(self.target)
        return None

    def _get_users_loaded(self):
        """Get the number of users loaded in the modal."""
        return self.page.evaluate('document.querySelector(\'div[class="_aano"]\').childNodes.item(0).childNodes.item(0).childElementCount')

    def _scroll_to_bottom(self, group):
        """Scroll the modal to the bottom."""
        scroll_tries = 0
        while scroll_tries < self.scroll_retries:
            users_loaded = self._get_users_loaded()
            self._scroll()
            new_users_loaded = self._get_users_loaded()
            print(f"\r⏳ Wait, getting {group}... {new_users_loaded} users loaded", end="", flush=True)
            if users_loaded == new_users_loaded:
                scroll_tries += 1
            else:
                scroll_tries = 0
        print(f"\r⏳ Wait, getting {group}... {new_users_loaded} users loaded")

    def _get_scroll_retries(self, default=6):
        """
        Get the number of retries for scrolling the modal. The default number of retries is 6.
        If the SCROLL_RETRIES argument is provided, it will be added to the default number of retries.
        """
        if not self.args.get(ArgumentOptions.SCROLL_RETRIES) is None:
            default += self.args.get(ArgumentOptions.SCROLL_RETRIES)
        return default

    def _scroll(self):
        """Scroll the modal by setting the scroll-top position to max."""
        self.page.evaluate('document.querySelector(\'div[class="_aano"]\').scrollTop = document.querySelector(\'div[class="_aano"]\').scrollTopMax')
        time.sleep(self.scroll_delay)

    def _get_scroll_delay(self, default=0.5):
        """
        Get the delay time for scrolling the modal. The default delay time is 0.5 seconds.
        If the SCROLL_DELAY argument is provided, it will be added to the default delay time.
        """
        if not self.args.get(ArgumentOptions.SCROLL_DELAY) is None:
            default += self.args.get(ArgumentOptions.SCROLL_DELAY)
        return default

    def _get_list(self):
        """Get the list of followers or following users from HTML content."""
        pattern = r'href="/([^/"]*?)/" role="link"'
        html_content = self.page.content()
        users = re.findall(pattern, html_content)
        return [value for value in list(set(users)) if value not in ["reels", "explore", self.target]]
