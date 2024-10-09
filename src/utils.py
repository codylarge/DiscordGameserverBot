from datetime import datetime
import os

def load_verified_users(VERIFIED_USERS_FILE, verified_users):
    if os.path.exists(VERIFIED_USERS_FILE):
        with open(VERIFIED_USERS_FILE, "r") as f:
            for line in f:
                username, profile_link, verification_date = line.strip().split(":", 3)
                verified_users[username] = (profile_link, verification_date)
        print(f"Loaded {len(verified_users)} verified users from file.")
    else:
        print(f"No verified users file found. Starting fresh.")

def save_verified_user(username, profile_link, VERIFIED_USERS_FILE, verification_date):
    with open(VERIFIED_USERS_FILE, "a") as f:
        f.write(f"{username}:{profile_link}:{verification_date}\n")

def save_verified_users(VERIFIED_USERS_FILE, verified_users):
    """ Save all verified users to the file. """
    with open(VERIFIED_USERS_FILE, "w") as f:
        for username, (profile_link, verification_date) in verified_users.items():
            f.write(f"{username}:{profile_link}:{verification_date}\n")

def is_valid_profile_link(profile_link: str) -> bool:
    """Check if the provided profile link is a valid Steam64 ID or a valid Steam profile link."""
    if len(profile_link) == 17 and profile_link.isdigit():
        return True  # Valid Steam64 ID
    elif "steamcommunity.com" in profile_link:
        return True  # Valid Steam profile link
    return False  # Invalid