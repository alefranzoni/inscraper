"""Collections for getting statistics about the collected group of users."""

def diff(users):
    """Returns a tuple with the users that don't follow you and the users you don't follow."""
    followers, following = users
    not_following_you = list(set(following) - set(followers))
    you_dont_follow = list(set(followers) - set(following))
    if len(not_following_you) == 0:
        print("🤩 Congratulations, everyone follows you!")
    else:
        print("🔦 Oops! Seems like someone doesn't follow you:")
        for index, user in enumerate(not_following_you):
            print(f"{index + 1}. {user}")
    return not_following_you, you_dont_follow
