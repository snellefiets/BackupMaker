"""
BackupMaker - Simple Backup Application with GUI
"""

import json
import os
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
from pathlib import Path
from typing import Optional


class Settings:
    """Manages application settings stored in user's home directory."""

    def __init__(self):
        # Settings file in user's home directory (not in project)
        self.settings_dir = Path.home() / ".backupmaker"
        self.settings_file = self.settings_dir / "settings.json"
        self.settings_dir.mkdir(exist_ok=True)

        self.source_folder: str = ""
        self.target_folder: str = ""
        self.max_backups: int = 5

        self.load()

    def load(self):
        """Load settings from file."""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.source_folder = data.get("source_folder", "")
                    self.target_folder = data.get("target_folder", "")
                    self.max_backups = data.get("max_backups", 5)
            except (json.JSONDecodeError, IOError):
                pass  # Use defaults if file is corrupted

    def save(self):
        """Save settings to file."""
        data = {
            "source_folder": self.source_folder,
            "target_folder": self.target_folder,
            "max_backups": self.max_backups
        }
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)


class BackupMaker:
    """Handles backup creation and management."""

    BACKUP_EXTENSION = ".zip"

    @staticmethod
    def create_backup(source_folder: str, target_folder: str) -> Optional[str]:
        """
        Create a ZIP backup of the source folder.

        Returns the path to the created backup file, or None on failure.
        """
        source = Path(source_folder)
        target = Path(target_folder)

        if not source.exists() or not source.is_dir():
            raise ValueError(f"Source folder does not exist: {source}")

        target.mkdir(parents=True, exist_ok=True)

        # Create filename with timestamp and source folder name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        source_name = source.name
        backup_name = f"{timestamp}_{source_name}{BackupMaker.BACKUP_EXTENSION}"
        backup_path = target / backup_name

        # Create ZIP archive
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in source.rglob('*'):
                if file.is_file():
                    arcname = file.relative_to(source)
                    zipf.write(file, arcname)

        return str(backup_path)

    @staticmethod
    def cleanup_old_backups(target_folder: str, source_folder: str, max_backups: int):
        """
        Remove old backups for a specific source folder, keeping only the most recent ones.
        """
        target = Path(target_folder)
        source_name = Path(source_folder).name
        if not target.exists():
            return

        # Find all backup files for this specific source folder
        backup_files = sorted(
            target.glob(f"*_{source_name}{BackupMaker.BACKUP_EXTENSION}"),
            key=lambda f: f.stat().st_mtime,
            reverse=True  # Newest first
        )

        # Delete old backups beyond the limit
        for old_backup in backup_files[max_backups:]:
            try:
                old_backup.unlink()
            except OSError:
                pass  # Ignore deletion errors

    @staticmethod
    def get_backup_count(target_folder: str, source_folder: str) -> int:
        """Get the number of existing backups for a specific source folder."""
        target = Path(target_folder)
        source_name = Path(source_folder).name
        if not target.exists():
            return 0

        backup_files = list(target.glob(f"*_{source_name}{BackupMaker.BACKUP_EXTENSION}"))
        return len(backup_files)


class BackupApp:
    """Main application GUI."""

    def __init__(self):
        self.settings = Settings()
        self.root = tk.Tk()
        self.root.title("BackupMaker")
        self.root.geometry("500x300")
        self.root.resizable(False, False)

        self._setup_ui()
        self._load_settings_to_ui()

    def _setup_ui(self):
        """Setup the user interface."""
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Source folder
        ttk.Label(main_frame, text="Source Ordner:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.source_var = tk.StringVar()
        source_entry = ttk.Entry(main_frame, textvariable=self.source_var, width=40)
        source_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="...", width=3, command=self._browse_source).grid(row=0, column=2, pady=5)

        # Target folder
        ttk.Label(main_frame, text="Target Ordner:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.target_var = tk.StringVar()
        target_entry = ttk.Entry(main_frame, textvariable=self.target_var, width=40)
        target_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="...", width=3, command=self._browse_target).grid(row=1, column=2, pady=5)

        # Max backups
        ttk.Label(main_frame, text="Max. Backups behalten:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.max_backups_var = tk.IntVar(value=5)
        max_spin = ttk.Spinbox(main_frame, from_=1, to=100, textvariable=self.max_backups_var, width=10)
        max_spin.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        # Status label
        self.status_var = tk.StringVar(value="Bereit")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, foreground="gray")
        status_label.grid(row=3, column=0, columnspan=3, pady=10)

        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=20)

        ttk.Button(button_frame, text="Backup erstellen", command=self._create_backup).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Einstellungen speichern", command=self._save_settings).pack(side=tk.LEFT, padx=10)

    def _browse_source(self):
        """Open folder browser for source."""
        folder = filedialog.askdirectory(title="Source Ordner auswählen")
        if folder:
            self.source_var.set(folder)
            self._update_status()

    def _browse_target(self):
        """Open folder browser for target."""
        folder = filedialog.askdirectory(title="Target Ordner auswählen")
        if folder:
            self.target_var.set(folder)
            self._update_status()

    def _load_settings_to_ui(self):
        """Load settings into UI fields."""
        self.source_var.set(self.settings.source_folder)
        self.target_var.set(self.settings.target_folder)
        self.max_backups_var.set(self.settings.max_backups)
        self._update_status()

    def _save_settings(self):
        """Save current UI values to settings."""
        self.settings.source_folder = self.source_var.get()
        self.settings.target_folder = self.target_var.get()
        self.settings.max_backups = self.max_backups_var.get()
        self.settings.save()
        messagebox.showinfo("Gespeichert", "Einstellungen wurden gespeichert!")

    def _update_status(self):
        """Update the status label."""
        source = self.source_var.get()
        target = self.target_var.get()
        if target and source:
            count = BackupMaker.get_backup_count(target, source)
            max_b = self.max_backups_var.get()
            source_name = Path(source).name
            self.status_var.set(f"Backups für '{source_name}': {count} / {max_b}")
        else:
            self.status_var.set("Bereit")

    def _create_backup(self):
        """Create a new backup."""
        source = self.source_var.get()
        target = self.target_var.get()
        max_backups = self.max_backups_var.get()

        # Validate inputs
        if not source:
            messagebox.showerror("Fehler", "Bitte Source Ordner auswählen!")
            return
        if not target:
            messagebox.showerror("Fehler", "Bitte Target Ordner auswählen!")
            return
        if not Path(source).exists():
            messagebox.showerror("Fehler", f"Source Ordner existiert nicht:\n{source}")
            return

        # Save settings before backup
        self._save_settings_silent()

        try:
            self.status_var.set("Backup wird erstellt...")
            self.root.update()

            # Create backup
            backup_path = BackupMaker.create_backup(source, target)

            # Cleanup old backups (only for this source folder)
            BackupMaker.cleanup_old_backups(target, source, max_backups)

            self._update_status()
            messagebox.showinfo("Erfolg", f"Backup erstellt:\n{backup_path}")

        except Exception as e:
            messagebox.showerror("Fehler", f"Backup fehlgeschlagen:\n{str(e)}")
            self.status_var.set("Fehler beim Backup!")

    def _save_settings_silent(self):
        """Save settings without showing message."""
        self.settings.source_folder = self.source_var.get()
        self.settings.target_folder = self.target_var.get()
        self.settings.max_backups = self.max_backups_var.get()
        self.settings.save()

    def run(self):
        """Start the application."""
        self.root.mainloop()


def main():
    app = BackupApp()
    app.run()


if __name__ == '__main__':
    main()
