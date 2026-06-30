# Configuration file for the diary application
import os
from pathlib import Path

# Application directories
APP_NAME = "PersonalDiary"
APP_DIR = Path.home() / f".{APP_NAME.lower()}"
DIARY_DIR = APP_DIR / "entries"
KEY_FILE = APP_DIR / "key.key"

# Encryption settings
ENCRYPTION_KEY_SIZE = 32  # 256 bits
SALT_SIZE = 16
NONCE_SIZE = 12
TAG_SIZE = 16

# Ensure directories exist
APP_DIR.mkdir(exist_ok=True)
DIARY_DIR.mkdir(exist_ok=True)

# File extensions
DIARY_EXTENSION = ".encrypted"

# Date format for filenames
DATE_FORMAT = "%Y-%m-%d_%H-%M-%S"
DISPLAY_DATE_FORMAT = "%B %d, %Y at %I:%M %p"
