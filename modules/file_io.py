"""
This module is responsible for handling the local files.
"""
from datetime import datetime
import os

def save(username, users, diff):
    """Saves the scraped data into a text file."""
    date = datetime.now().strftime('%Y%m%d_%H%M%S')
    path = f'{_target_directory(username)}/{date}.txt'
    _write(path, users, diff)

def _target_directory(username):
    """Returns the target directory for the given username."""
    return f'reports/{username}'

def _write(path, data, diff):
    """Writes a text file with the given data into a specific path."""
    followers, following = data
    not_following_you, you_dont_follow = diff
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(f'Followers: {followers}\n')
        f.write(f'\nFollowing: {following}\n')
        f.write(f'\nNot following you: {not_following_you}\n')
        f.write(f'\nYou don\'t follow: {you_dont_follow}\n')
