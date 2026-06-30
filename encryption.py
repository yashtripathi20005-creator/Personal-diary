# Encryption utilities for the diary application
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
import hashlib
from config import SALT_SIZE, NONCE_SIZE, ENCRYPTION_KEY_SIZE, KEY_FILE
from pathlib import Path


class DiaryEncryption:
    """Handles encryption and decryption of diary entries"""
    
    def __init__(self, password: str):
        self.password = password
        self.salt = None
        self.key = None
        self.fernet = None
        self._initialize_encryption()
    
    def _initialize_encryption(self):
        """Initialize encryption with password"""
        # Try to load existing salt or create new one
        if KEY_FILE.exists():
            with open(KEY_FILE, 'rb') as f:
                data = f.read()
                self.salt = data[:SALT_SIZE]
                self.key = data[SALT_SIZE:]
                self.fernet = Fernet(self.key)
        else:
            # Generate new salt and key
            self.salt = os.urandom(SALT_SIZE)
            self.key = self._derive_key(self.password, self.salt)
            self.fernet = Fernet(self.key)
            # Save salt and key
            with open(KEY_FILE, 'wb') as f:
                f.write(self.salt + self.key)
    
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key from password and salt"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=ENCRYPTION_KEY_SIZE,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt_text(self, text: str) -> bytes:
        """Encrypt text using Fernet symmetric encryption"""
        if not self.fernet:
            raise ValueError("Encryption not initialized")
        return self.fernet.encrypt(text.encode('utf-8'))
    
    def decrypt_text(self, encrypted_data: bytes) -> str:
        """Decrypt encrypted data using Fernet symmetric encryption"""
        if not self.fernet:
            raise ValueError("Encryption not initialized")
        decrypted = self.fernet.decrypt(encrypted_data)
        return decrypted.decode('utf-8')
    
    def change_password(self, old_password: str, new_password: str) -> bool:
        """Change the encryption password"""
        try:
            # Verify old password works
            test_encryption = DiaryEncryption(old_password)
            test_encryption.fernet.decrypt(
                test_encryption.fernet.encrypt(b"test")
            )
            
            # Create new encryption with new password
            new_salt = os.urandom(SALT_SIZE)
            new_key = self._derive_key(new_password, new_salt)
            
            # Save new salt and key
            with open(KEY_FILE, 'wb') as f:
                f.write(new_salt + new_key)
            
            # Update current instance
            self.salt = new_salt
            self.key = new_key
            self.fernet = Fernet(new_key)
            self.password = new_password
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def reencrypt_all_entries(old_password: str, new_password: str) -> bool:
        """Re-encrypt all diary entries with new password"""
        from diary import Diary
        from config import DIARY_DIR
        
        try:
            # Create old and new encryption instances
            old_enc = DiaryEncryption(old_password)
            new_enc = DiaryEncryption(new_password)
            
            # Get all diary entries
            diary = Diary()
            entries = diary.get_all_entries()
            
            # Re-encrypt each entry
            for entry in entries:
                encrypted_content = old_enc.decrypt_text(entry.content)
                new_encrypted = new_enc.encrypt_text(encrypted_content)
                
                # Save with new encryption
                file_path = DIARY_DIR / f"{entry.filename}{Diary.EXTENSION}"
                with open(file_path, 'wb') as f:
                    f.write(new_encrypted)
            
            return True
        except Exception:
            return False
