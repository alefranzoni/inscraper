import re, time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

BASE_URL = "https://www.instagram.com/"
FOLLOWERS_URL = BASE_URL + "{}/followers/"
FOLLOWING_URL = BASE_URL + "{}/following/"

class Scraper(object):
    """Playwright based Instagram scraper. 
    It's able to start up a browser, authenticate to Instagram and get the followers/following list from a specific user given."""
    
    def __init__(self, headless=True):
        """Initialize the Scraper object."""
        
        print("🚀 The environment is getting ready...")
        self.headless = headless
        self.browser = sync_playwright().start()

    def close(self):
        """Close the browser."""

        self.browser.close()   
        
    def authenticate(self, username, password):
        """Authenticate to Instagram with the provided credentials."""

        print("🌎 Navigating to Instagram page")

        self.target = username
        self.browser = self.browser.firefox.launch(headless=self.headless)
        self.page = self.browser.new_page()
        self.page.goto(BASE_URL, wait_until="domcontentloaded")
        
        print("🔒 Starting the authentication process...")

        try:
            self.page.wait_for_selector('button[type="submit"]', timeout=5000)
            self.page.fill('input[name="username"]', username)
            self.page.fill('input[name="password"]', password)
            self.page.click('button[type="submit"]')
            
            if self._check_protection_auth():
                print("🔐 Two factor authentication is required")
                auth_code = input("🔑 Enter the 2FA code: ")
                self.page.fill('input[name="verificationCode"]', auth_code)
                self.page.click('button[type="button"]')
            
            self.page.wait_for_function('() => window.location.href.includes("accounts/onetap")', timeout=5000)
            print("🔓 Successful login")
            return True
        except PlaywrightTimeoutError:
            print("🧐 Oops! Seems it's taking more than usual to load the login page. Try again later")
            self.close()
            return False
        
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
            self.page.wait_for_function('() => window.location.href.includes("login/two_factor")', timeout=5000)
            return True
        except PlaywrightTimeoutError:
            return False
        
    def _open_modal(self, link):
        """Open the modal with the list of followers or following users."""

        self.page.goto(link, wait_until="domcontentloaded")
        self.page.wait_for_selector("div[class='_aano']")
        time.sleep(1)

    def _get_link(self, group):
        """Get the link to the followers or following list."""

        print("👥 Openening {} list".format(group))

        if group == "followers":
            return FOLLOWERS_URL.format(self.target)
        elif group == "following":
            return FOLLOWING_URL.format(self.target)
        else:
            return None
        
    def _get_users_loaded(self):
        """Get the number of users loaded in the modal."""

        return self.page.evaluate('document.querySelector(\'div[class="_aano"]\').childNodes.item(0).childNodes.item(0).childElementCount')

    def _scroll_to_bottom(self, list):
        """Scroll the modal to the bottom."""

        scroll_tries = 0
        while scroll_tries < 6:
            users_loaded = self._get_users_loaded()
            self._scroll()
            new_users_loaded = self._get_users_loaded()

            print(f"\r⏳ Wait, getting {list}... {new_users_loaded} users loaded", end="", flush=True)

            if (users_loaded == new_users_loaded):
                scroll_tries += 1
            else:
                scroll_tries = 0
        
        print(f"\r⏳ Wait, getting {list}... {new_users_loaded} users loaded")
    
    def _scroll(self):
        """Scroll the modal by setting the scroll-top position to max."""

        self.page.evaluate('document.querySelector(\'div[class="_aano"]\').scrollTop = document.querySelector(\'div[class="_aano"]\').scrollTopMax')
        time.sleep(.5)

    def _get_list(self):
        """Get the list of followers or following users from HTML content."""

        pattern = r'href="/([^/"]*?)/" role="link"'
        html_content = self.page.content()
        users = re.findall(pattern, html_content)
        
        return [value for value in list(set(users)) if value not in ["reels", "explore", self.target]]