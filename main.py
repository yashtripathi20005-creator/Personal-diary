# Main application entry point
import sys
import getpass
from pathlib import Path
from diary import Diary
from config import APP_NAME, DIARY_DIR


def clear_screen():
    """Clear the terminal screen"""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header():
    """Print the application header"""
    print("=" * 60)
    print(f"  {APP_NAME} - Secure Personal Diary")
    print("=" * 60)
    print()


def print_entry(entry, show_full=False):
    """Print a diary entry"""
    print(f"\n📝 {entry.title}")
    print(f"📅 {entry.date_display}")
    print("-" * 50)
    if show_full:
        print(entry.content)
    else:
        print(entry.preview)
        if len(entry.content) > 200:
            print("\n... (Use 'view' command to see full entry)")
    print("-" * 50)


def main():
    """Main application loop"""
    clear_screen()
    print_header()
    
    # Check if encryption key exists
    from config import KEY_FILE
    if not KEY_FILE.exists():
        print("🔐 First time setup - Create your password")
        password = getpass.getpass("Enter a strong password: ")
        confirm = getpass.getpass("Confirm password: ")
        
        if password != confirm:
            print("❌ Passwords do not match. Exiting...")
            sys.exit(1)
        
        if len(password) < 8:
            print("❌ Password must be at least 8 characters. Exiting...")
            sys.exit(1)
        
        diary = Diary(password)
        print("✅ Password created successfully!")
    else:
        # Login
        print("🔐 Enter your password to access your diary")
        attempts = 3
        while attempts > 0:
            password = getpass.getpass("Password: ")
            try:
                diary = Diary(password)
                # Test encryption
                diary.encryption.fernet.decrypt(
                    diary.encryption.fernet.encrypt(b"test")
                )
                print("✅ Login successful!")
                break
            except Exception:
                attempts -= 1
                print(f"❌ Wrong password! {attempts} attempts remaining")
                if attempts == 0:
                    print("❌ Too many failed attempts. Exiting...")
                    sys.exit(1)
    
    # Main menu loop
    while True:
        clear_screen()
        print_header()
        
        # Show stats
        entry_count = diary.get_entry_count()
        print(f"📊 Total entries: {entry_count}")
        print()
        
        # Show recent entries
        if entry_count > 0:
            print("📋 Recent entries:")
            entries = diary.get_all_entries()
            for i, entry in enumerate(entries[:5], 1):
                print(f"  {i}. {entry.title}")
                print(f"     📅 {entry.date_display}")
            if entry_count > 5:
                print(f"  ... and {entry_count - 5} more")
            print()
        
        # Menu options
        print("Available commands:")
        print("  📝 new     - Create a new diary entry")
        print("  📖 list    - List all entries")
        print("  🔍 search  - Search entries")
        print("  👀 view    - View a specific entry")
        print("  ✏️ edit    - Edit an entry")
        print("  🗑️ delete  - Delete an entry")
        print("  🔑 change  - Change password")
        print("  ❌ exit    - Exit the diary")
        print()
        
        command = input("Enter command: ").strip().lower()
        
        if command == "new":
            create_new_entry(diary)
        elif command == "list":
            list_entries(diary)
        elif command == "search":
            search_entries(diary)
        elif command == "view":
            view_entry(diary)
        elif command == "edit":
            edit_entry(diary)
        elif command == "delete":
            delete_entry(diary)
        elif command == "change":
            change_password(diary)
        elif command in ["exit", "quit"]:
            print("👋 Goodbye!")
            sys.exit(0)
        else:
            print("❌ Unknown command. Press Enter to continue...")
            input()
    
    return 0


def create_new_entry(diary):
    """Create a new diary entry"""
    clear_screen()
    print_header()
    print("📝 New Diary Entry")
    print("=" * 60)
    print("Enter your entry (type 'END' on a new line to finish, or 'CANCEL' to cancel):")
    print()
    
    lines = []
    while True:
        line = input()
        if line == "END":
            break
        if line == "CANCEL":
            print("❌ Entry cancelled.")
            input("Press Enter to continue...")
            return
        
        lines.append(line)
    
    if not lines:
        print("❌ Empty entry not saved.")
        input("Press Enter to continue...")
        return
    
    content = "\n".join(lines)
    entry = diary.add_entry(content)
    print(f"\n✅ Entry saved successfully!")
    print(f"📅 {entry.date_display}")
    input("\nPress Enter to continue...")


def list_entries(diary):
    """List all diary entries"""
    clear_screen()
    print_header()
    print("📖 All Diary Entries")
    print("=" * 60)
    
    entries = diary.get_all_entries()
    if not entries:
        print("No entries found.")
        input("\nPress Enter to continue...")
        return
    
    for i, entry in enumerate(entries, 1):
        print(f"\n{i}. {entry.title}")
        print(f"   📅 {entry.date_display}")
        print(f"   📄 {entry.preview}")
    
    print(f"\n📊 Total: {len(entries)} entries")
    input("\nPress Enter to continue...")


def search_entries(diary):
    """Search diary entries"""
    clear_screen()
    print_header()
    print("🔍 Search Entries")
    print("=" * 60)
    
    query = input("Enter search term: ").strip()
    if not query:
        print("❌ No search term entered.")
        input("Press Enter to continue...")
        return
    
    results = diary.search_entries(query)
    
    if not results:
        print(f"❌ No entries found containing '{query}'")
        input("\nPress Enter to continue...")
        return
    
    print(f"\n✅ Found {len(results)} entries containing '{query}':")
    for i, entry in enumerate(results, 1):
        print(f"\n{i}. {entry.title}")
        print(f"   📅 {entry.date_display}")
        print(f"   📄 {entry.preview}")
    
    input("\nPress Enter to continue...")


def view_entry(diary):
    """View a specific diary entry"""
    clear_screen()
    print_header()
    print("👀 View Entry")
    print("=" * 60)
    
    entries = diary.get_all_entries()
    if not entries:
        print("No entries found.")
        input("\nPress Enter to continue...")
        return
    
    print("Recent entries:")
    for i, entry in enumerate(entries[:10], 1):
        print(f"{i}. {entry.title} - {entry.date_display}")
    
    try:
        choice = int(input(f"\nSelect entry (1-{min(10, len(entries))}): "))
        if 1 <= choice <= min(10, len(entries)):
            entry = entries[choice - 1]
            clear_screen()
            print_header()
            print(f"📝 {entry.title}")
            print(f"📅 {entry.date_display}")
            print("=" * 60)
            print(entry.content)
            print("=" * 60)
            input("\nPress Enter to continue...")
        else:
            print("❌ Invalid selection.")
            input("Press Enter to continue...")
    except ValueError:
        print("❌ Invalid input.")
        input("Press Enter to continue...")


def edit_entry(diary):
    """Edit a diary entry"""
    clear_screen()
    print_header()
    print("✏️ Edit Entry")
    print("=" * 60)
    
    entries = diary.get_all_entries()
    if not entries:
        print("No entries found.")
        input("\nPress Enter to continue...")
        return
    
    print("Recent entries:")
    for i, entry in enumerate(entries[:10], 1):
        print(f"{i}. {entry.title} - {entry.date_display}")
    
    try:
        choice = int(input(f"\nSelect entry to edit (1-{min(10, len(entries))}): "))
        if 1 <= choice <= min(10, len(entries)):
            entry = entries[choice - 1]
            clear_screen()
            print_header()
            print(f"✏️ Editing: {entry.title}")
            print(f"📅 {entry.date_display}")
            print("=" * 60)
            print("Current content:")
            print(entry.content)
            print("=" * 60)
            print("\nEnter new content (type 'END' on a new line to finish, or 'CANCEL' to cancel):")
            
            lines = []
            while True:
                line = input()
                if line == "END":
                    break
                if line == "CANCEL":
                    print("❌ Edit cancelled.")
                    input("Press Enter to continue...")
                    return
                lines.append(line)
            
            if not lines:
                print("❌ Empty content not saved.")
                input("Press Enter to continue...")
                return
            
            new_content = "\n".join(lines)
            if diary.edit_entry(entry.filename, new_content):
                print("✅ Entry updated successfully!")
            else:
                print("❌ Failed to update entry.")
            input("Press Enter to continue...")
        else:
            print("❌ Invalid selection.")
            input("Press Enter to continue...")
    except ValueError:
        print("❌ Invalid input.")
        input("Press Enter to continue...")


def delete_entry(diary):
    """Delete a diary entry"""
    clear_screen()
    print_header()
    print("🗑️ Delete Entry")
    print("=" * 60)
    
    entries = diary.get_all_entries()
    if not entries:
        print("No entries found.")
        input("\nPress Enter to continue...")
        return
    
    print("Recent entries:")
    for i, entry in enumerate(entries[:10], 1):
        print(f"{i}. {entry.title} - {entry.date_display}")
    
    try:
        choice = int(input(f"\nSelect entry to delete (1-{min(10, len(entries))}): "))
        if 1 <= choice <= min(10, len(entries)):
            entry = entries[choice - 1]
            confirm = input(f"Are you sure you want to delete '{entry.title}'? (y/n): ")
            if confirm.lower() == 'y':
                if diary.delete_entry(entry.filename):
                    print("✅ Entry deleted successfully!")
                else:
                    print("❌ Failed to delete entry.")
            else:
                print("❌ Deletion cancelled.")
            input("Press Enter to continue...")
        else:
            print("❌ Invalid selection.")
            input("Press Enter to continue...")
    except ValueError:
        print("❌ Invalid input.")
        input("Press Enter to continue...")


def change_password(diary):
    """Change the encryption password"""
    clear_screen()
    print_header()
    print("🔑 Change Password")
    print("=" * 60)
    
    old_password = getpass.getpass("Enter current password: ")
    new_password = getpass.getpass("Enter new password: ")
    confirm = getpass.getpass("Confirm new password: ")
    
    if new_password != confirm:
        print("❌ Passwords do not match.")
        input("Press Enter to continue...")
        return
    
    if len(new_password) < 8:
        print("❌ Password must be at least 8 characters.")
        input("Press Enter to continue...")
        return
    
    # Re-encrypt all entries with new password
    from encryption import DiaryEncryption
    
    if DiaryEncryption.reencrypt_all_entries(old_password, new_password):
        print("✅ Password changed successfully!")
        print("✅ All entries re-encrypted with new password.")
    else:
        print("❌ Failed to change password. Please check your current password.")
    
    input("Press Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        sys.exit(1)
