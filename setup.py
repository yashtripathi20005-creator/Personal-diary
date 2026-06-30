#!/usr/bin/env python3
"""
Setup script for the Personal Diary application
"""

import os
from pathlib import Path
import sys


def setup():
    """Create necessary directories and files for the diary application"""
    print("🔧 Setting up Personal Diary Application...")
    print("=" * 50)
    
    # Create config
    from config import APP_DIR, DIARY_DIR, KEY_FILE
    
    print(f"✅ Application directory: {APP_DIR}")
    print(f"✅ Diary directory: {DIARY_DIR}")
    
    if KEY_FILE.exists():
        print("ℹ️  Encryption key already exists.")
    else:
        print("ℹ️  No encryption key found. Will be created on first run.")
    
    print("\n✅ Setup complete!")
    print("\nTo run the diary application:")
    print("  python main.py")
    print("\nYour diary entries will be encrypted and stored in:")
    print(f"  {DIARY_DIR}")


def check_requirements():
    """Check if required packages are installed"""
    try:
        import cryptography
        print("✅ Required packages are installed.")
        return True
    except ImportError:
        print("❌ Required packages are not installed.")
        print("\nPlease install them using:")
        print("  pip install -r requirements.txt")
        return False


if __name__ == "__main__":
    if not check_requirements():
        sys.exit(1)
    
    setup()
    sys.exit(0)
