# BackupMaker

A simple backup application with GUI that creates timestamped ZIP backups of folders.

## Features

- **Source & Target Selection**: Choose which folder to backup and where to store backups
- **Timestamped Backups**: Backups are named `YYYYMMDD_HHMMSS_FolderName.zip`
- **Automatic Cleanup**: Keeps only the last N backups per source folder (configurable)
- **Persistent Settings**: Settings are saved automatically and restored on next launch
- **Desktop Shortcut**: Quick access via batch file

## Requirements

- Python 3.x
- tkinter (included with Python on Windows)

## Installation

```bash
pip install -e .
```

## Usage

### GUI Application

Run the backup application with GUI:

```bash
python src/backup_app.py
```

Or use the desktop shortcut `BackupMaker.bat` (if created).

### How it works

1. **Source Folder**: Select the folder you want to backup
2. **Target Folder**: Select where to save the ZIP backups
3. **Max. Backups to keep**: Set how many backups to retain (older ones are deleted automatically)
4. **Create Backup**: Click to create a new backup
5. **Save Settings**: Save your current configuration

Settings are stored in `~/.backupmaker/settings.json` (user home directory).

### CLI Zipper Tool

The project also includes a command-line ZIP utility:

```bash
# Create ZIP
python src/zipper.py create archive.zip -f file1.txt file2.txt -d folder/

# Extract ZIP
python src/zipper.py extract archive.zip ./output/

# List contents
python src/zipper.py list archive.zip
```

## Project Structure

```
BackupMaker/
├── src/
│   ├── backup_app.py   # Main GUI application
│   └── zipper.py       # CLI ZIP utility
├── pyproject.toml
└── README.md
```
