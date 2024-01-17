"""
This module is responsible for handling cookies in a Playwright session.
"""
import json
import os
import sys
from cryptography.fernet import Fernet

KEY_PATH = 'data/passkey.key'
COOKIES_PATH = 'data/cookies.json'

def handle_security_key(generate_key_arg):
    """
    Handles the existence and generation of a security key based on 
    the provided argument.
    """
    key_exists=check_security_key_exists()
    if not key_exists and not generate_key_arg:
        print("🚨 The security key has not been found. Generate or place it inside the data folder."
            "\n → More information at https://github.com/alefranzoni/inscraper")
        sys.exit()
    elif generate_key_arg:
        if key_exists:
            generate_new_key = ""
            while generate_new_key not in ["y", "n"]:
                generate_new_key = input(
                    "🚨 You have already generated a security key! "
                    "Do you want to generate a new one and replace it? (y/n): "
                ).lower().strip()
            if generate_new_key == "y":
                generate_security_key()
        else:
            generate_security_key()

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

def get_cookies():
    """Retrieves the current cookies."""
    if os.path.exists(COOKIES_PATH):
        with open(COOKIES_PATH, 'r', encoding='utf-8') as f:
            cookies_encrypted = f.read()
        with open(KEY_PATH, 'rb') as file:
            passkey = file.read()
            cypher = Fernet(passkey)
        cookies_bytes = cypher.decrypt(cookies_encrypted)
        cookies = json.loads(cookies_bytes.decode('utf-8'))
        return cookies
    return None

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
