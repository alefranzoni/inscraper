"""
This module is responsible for handling cookies in a Playwright session.
"""
import json
import os
from cryptography.fernet import Fernet

KEY_PATH = 'data/passkey.key'
COOKIES_PATH = 'data/cookies.json'

def check_security_key_exists():
    """This function checks if the security key file exists at the project data folder."""
    if not os.path.exists(KEY_PATH):
        return False
    return True

def generate_security_key():
    """Generates the security key needed to encrypt and decrypt local files."""
    print("🔐 The new security key is being generated...")
    passkey = Fernet.generate_key()
    os.makedirs('data', exist_ok=True)
    with open(KEY_PATH, 'wb') as file:
        file.write(passkey)

def add_cookies(context):
    """Checks for the existence of cookies file and loads it to the browser context."""
    if os.path.exists(COOKIES_PATH):
        with open(COOKIES_PATH, 'r', encoding='utf-8') as f:
            cookies_encrypted = f.read()

        with open(KEY_PATH, 'rb') as file:
            passkey = file.read()
            cypher = Fernet(passkey)

        cookies_bytes = cypher.decrypt(cookies_encrypted)
        cookies = json.loads(cookies_bytes.decode('utf-8'))
        context.add_cookies(cookies=cookies)

def save_cookies(context):
    """Saves the cookies from the browser context."""
    with open(KEY_PATH, 'rb') as file:
        passkey = file.read()
        cypher = Fernet(passkey)
    cookies_json = json.dumps(context.cookies())
    cookies_bytes = cookies_json.encode('utf-8')
    cookies_encrypted = cypher.encrypt(cookies_bytes)

    with open(COOKIES_PATH, 'wb') as f:
        f.write(cookies_encrypted)
