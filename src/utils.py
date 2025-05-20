import re

language_mapping = {
    "en": "english",
    "es": "spanish",
    "fr": "french",
    "de": "german",
    "it": "italian",
    "pt": "portuguese",
    "pl": "polish",
    "tr": "turkish",
    "ru": "russian",
    "nl": "dutch",
    "cs": "czech",
    "ar": "arabic",
    "zh-cn": "chinese", # Note: Whisper might use 'zh', googletrans 'zh-cn' or 'zh-tw'
    "ja": "japanese",
    "hu": "hungarian",
    "ko": "korean"
    # Add more as needed, ensure codes are compatible between Whisper and target services
}

# YouTube link validation
YOUTUBE_LINK_REGEX = r"^(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[^&\s]+$"

def is_valid_youtube_link(link):
    """
    Validates a YouTube link using a regex pattern.
    Args:
        link (str): The YouTube link to validate.
    Returns:
        bool: True if the link is valid, False otherwise.
    """
    if not link: # Ensure link is not None or empty before matching
        return False
    return bool(re.match(YOUTUBE_LINK_REGEX, link))
