import os
import json
import shutil
import tempfile
from datetime import datetime
from filelock import FileLock
from config import Config

class JSONStorage:
    """
    Centralized JSON storage manager with safe concurrent updates,
    file locking, atomic file replacement, and automatic backup integration.
    """
    
    def __init__(self, data_dir=None):
        self.data_dir = data_dir or Config.DATA_DIR
        self.backup_dir = os.path.join(self.data_dir, 'backups')
        self._ensure_directories()

    def _ensure_directories(self):
        """Create storage and backup directories if they don't exist."""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)

    def _get_lock_path(self, filepath):
        """Generate path for the filelock file."""
        return f"{filepath}.lock"

    def read(self, filepath, default=None):
        """
        Safely read JSON data from file with shared/exclusive locking.
        Returns default (list or dict) if file doesn't exist or is empty.
        """
        if default is None:
            default = []
            
        if not os.path.exists(filepath):
            return default

        lock_path = self._get_lock_path(filepath)
        try:
            with FileLock(lock_path, timeout=5):
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if not content:
                        return default
                    return json.loads(content)
        except Exception as e:
            print(f"[JSONStorage Error] Failed to read {filepath}: {e}")
            return default

    def write(self, filepath, data):
        """
        Safely write data to JSON file using an atomic replace pattern:
        Writes to a temporary file first, then atomically renames to target.
        Guarantees that a crash or interrupted write never corrupts storage.
        """
        self._ensure_directories()
        lock_path = self._get_lock_path(filepath)
        
        with FileLock(lock_path, timeout=10):
            # Create a temporary file in the same directory to allow atomic rename
            dir_name = os.path.dirname(filepath)
            with tempfile.NamedTemporaryFile('w', dir=dir_name, delete=False, encoding='utf-8') as tf:
                temp_name = tf.name
                json.dump(data, tf, indent=2, ensure_ascii=False)
                tf.flush()
                os.fsync(tf.fileno())
                
            # Atomically replace target file
            shutil.move(temp_name, filepath)
        return True

    def find_all(self, filepath):
        """Return all items from a collection JSON file."""
        return self.read(filepath, default=[])

    def find_by_id(self, filepath, item_id):
        """Find a single item by its 'id' field."""
        items = self.find_all(filepath)
        for item in items:
            if item.get('id') == item_id:
                return item
        return None

    def find_where(self, filepath, predicate):
        """Find all items matching a predicate function."""
        items = self.find_all(filepath)
        return [item for item in items if predicate(item)]

    def insert(self, filepath, item):
        """Insert a single item into a JSON list collection."""
        items = self.find_all(filepath)
        items.append(item)
        self.write(filepath, items)
        return item

    def update(self, filepath, item_id, updates):
        """
        Update an item by its 'id' with key-value updates.
        Returns the updated item or None if not found.
        """
        items = self.find_all(filepath)
        updated_item = None
        for i, item in enumerate(items):
            if item.get('id') == item_id:
                items[i].update(updates)
                items[i]['updated_at'] = datetime.utcnow().isoformat()
                updated_item = items[i]
                break
        if updated_item:
            self.write(filepath, items)
        return updated_item

    def delete(self, filepath, item_id):
        """Delete an item by its 'id'."""
        items = self.find_all(filepath)
        initial_len = len(items)
        items = [item for item in items if item.get('id') != item_id]
        if len(items) < initial_len:
            self.write(filepath, items)
            return True
        return False

# Global shared storage singleton
storage = JSONStorage()
