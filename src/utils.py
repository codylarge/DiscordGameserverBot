from datetime import datetime
import os

def is_valid_profile_link(profile_link: str) -> bool:
    """Check if the provided profile link is a valid Steam64 ID or a valid Steam profile link."""
    if len(profile_link) == 17 and profile_link.isdigit():
        return True  # Valid Steam64 ID
    elif "steamcommunity.com" in profile_link:
        return True  # Valid Steam profile link
    return False  # Invalid

