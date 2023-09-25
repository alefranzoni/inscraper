from datetime import datetime
import os

def save(username, users, diff):
    """Saves the scraped data into a text file."""

    date = datetime.now().strftime('%Y%m%d_%H%M%S')
    path = '{}/{}.txt'.format(_target_directory(username), date)
    
    return _write(path, users, diff)

def _target_directory(username):
    """Returns the target directory for the given username."""
  
    return 'reports/{}'.format(username)

def _write(path, data, diff):
    """Writes a text file with the given data into a specific path."""
    followers, following = data
    not_following_you, you_dont_follow = diff

    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        with open(path, 'w') as f:
            f.write('Followers: {}\n'.format(followers))
            f.write('\nFollowing: {}\n'.format(following))
            f.write('\nNot following you: {}\n'.format(not_following_you))
            f.write('\nYou don\'t follow: {}\n'.format(you_dont_follow))
        return True
    except:
        return False