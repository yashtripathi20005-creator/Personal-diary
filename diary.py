# Main diary functionality
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import json
import re
from config import DIARY_DIR, DATE_FORMAT, DISPLAY_DATE_FORMAT, DIARY_EXTENSION
from encryption import DiaryEncryption


class DiaryEntry:
    """Represents a single diary entry"""
    
    def __init__(self, filename: str, content: str, timestamp: datetime = None):
        self.filename = filename
        self.content = content
        if timestamp is None:
            self.timestamp = datetime.now()
        else:
            self.timestamp = timestamp
    
    @property
    def title(self) -> str:
        """Generate a title from the first line of content"""
        first_line = self.content.split('\n')[0] if self.content else "Untitled"
        return first_line[:50] + ("..." if len(first_line) > 50 else "")
    
    @property
    def date_display(self) -> str:
        """Display formatted date"""
        return self.timestamp.strftime(DISPLAY_DATE_FORMAT)
    
    @property
    def preview(self) -> str:
        """Get a preview of the entry (first 200 characters)"""
        preview_text = self.content[:200]
        if len(self.content) > 200:
            preview_text += "..."
        return preview_text
    
    def to_dict(self) -> dict:
        """Convert entry to dictionary for JSON serialization"""
        return {
            "filename": self.filename,
            "timestamp": self.timestamp.isoformat(),
            "content": self.content
        }


class Diary:
    """Main diary management class"""
    
    EXTENSION = DIARY_EXTENSION
    
    def __init__(self, password: str = None):
        self.password = password
        self.encryption = None
        if password:
            self.encryption = DiaryEncryption(password)
    
    def set_password(self, password: str):
        """Set or change the encryption password"""
        self.password = password
        self.encryption = DiaryEncryption(password)
    
    def add_entry(self, content: str) -> DiaryEntry:
        """Add a new diary entry"""
        if not self.encryption:
            raise ValueError("Please set a password first using set_password()")
        
        timestamp = datetime.now()
        filename = timestamp.strftime(DATE_FORMAT)
        
        # Encrypt the content
        encrypted_content = self.encryption.encrypt_text(content)
        
        # Save to file
        file_path = DIARY_DIR / f"{filename}{self.EXTENSION}"
        with open(file_path, 'wb') as f:
            f.write(encrypted_content)
        
        return DiaryEntry(filename, content, timestamp)
    
    def get_entry(self, filename: str) -> Optional[DiaryEntry]:
        """Retrieve a specific diary entry by filename"""
        if not self.encryption:
            raise ValueError("Please set a password first using set_password()")
        
        file_path = DIARY_DIR / f"{filename}{self.EXTENSION}"
        if not file_path.exists():
            return None
        
        # Read and decrypt
        with open(file_path, 'rb') as f:
            encrypted_content = f.read()
        
        try:
            content = self.encryption.decrypt_text(encrypted_content)
            # Try to extract timestamp from filename
            try:
                timestamp = datetime.strptime(filename, DATE_FORMAT)
            except ValueError:
                timestamp = datetime.now()
            
            return DiaryEntry(filename, content, timestamp)
        except Exception:
            return None
    
    def get_all_entries(self) -> List[DiaryEntry]:
        """Get all diary entries sorted by date (newest first)"""
        if not self.encryption:
            raise ValueError("Please set a password first using set_password()")
        
        entries = []
        for file_path in DIARY_DIR.glob(f"*{self.EXTENSION}"):
            filename = file_path.stem
            entry = self.get_entry(filename)
            if entry:
                entries.append(entry)
        
        # Sort by timestamp (newest first)
        entries.sort(key=lambda x: x.timestamp, reverse=True)
        return entries
    
    def search_entries(self, query: str) -> List[DiaryEntry]:
        """Search diary entries for a specific text"""
        all_entries = self.get_all_entries()
        results = []
        
        for entry in all_entries:
            if query.lower() in entry.content.lower():
                results.append(entry)
        
        return results
    
    def delete_entry(self, filename: str) -> bool:
        """Delete a diary entry"""
        file_path = DIARY_DIR / f"{filename}{self.EXTENSION}"
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    
    def edit_entry(self, filename: str, new_content: str) -> bool:
        """Edit an existing diary entry"""
        if not self.encryption:
            raise ValueError("Please set a password first using set_password()")
        
        file_path = DIARY_DIR / f"{filename}{self.EXTENSION}"
        if not file_path.exists():
            return False
        
        # Encrypt and save new content
        encrypted_content = self.encryption.encrypt_text(new_content)
        with open(file_path, 'wb') as f:
            f.write(encrypted_content)
        
        return True
    
    def get_entry_count(self) -> int:
        """Get the number of diary entries"""
        return len(list(DIARY_DIR.glob(f"*{self.EXTENSION}")))
