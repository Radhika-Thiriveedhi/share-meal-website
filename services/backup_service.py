import os
import shutil
import zipfile
from datetime import datetime
from config import Config

class BackupService:
    @staticmethod
    def create_backup():
        """
        Creates a timestamped snapshot zip archive of all active JSON databases.
        Returns the path to the created backup archive.
        """
        os.makedirs(Config.BACKUP_DIR, exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"sharemeal_backup_{timestamp}.zip"
        backup_path = os.path.join(Config.BACKUP_DIR, backup_filename)

        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(Config.DATA_DIR):
                if Config.BACKUP_DIR in root:
                    continue
                for file in files:
                    if file.endswith('.json'):
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, Config.DATA_DIR)
                        zipf.write(file_path, arcname)
        return backup_filename

    @staticmethod
    def list_backups():
        """List all available backup archives with size and timestamp."""
        if not os.path.exists(Config.BACKUP_DIR):
            return []
        backups = []
        for f in os.listdir(Config.BACKUP_DIR):
            if f.endswith('.zip'):
                full_path = os.path.join(Config.BACKUP_DIR, f)
                stats = os.stat(full_path)
                backups.append({
                    "filename": f,
                    "size_bytes": stats.st_size,
                    "size_kb": round(stats.st_size / 1024, 2),
                    "created_at": datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                })
        backups.sort(key=lambda x: x["created_at"], reverse=True)
        return backups
