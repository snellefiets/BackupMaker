"""
ZIP utility for packing and unpacking files.
"""

import zipfile
from pathlib import Path
from typing import List, Optional


def create_zip(
    output_path: str,
    files: Optional[List[str]] = None,
    folders: Optional[List[str]] = None,
    compression: int = zipfile.ZIP_DEFLATED
) -> str:
    """
    Create a ZIP archive from files and/or folders.

    Args:
        output_path: Path for the output ZIP file
        files: List of file paths to include
        folders: List of folder paths to include (recursive)
        compression: Compression method (ZIP_DEFLATED, ZIP_STORED, ZIP_BZIP2, ZIP_LZMA)

    Returns:
        Path to the created ZIP file
    """
    with zipfile.ZipFile(output_path, 'w', compression) as zipf:
        if files:
            for file_path in files:
                path = Path(file_path)
                if path.is_file():
                    zipf.write(path, path.name)

        if folders:
            for folder_path in folders:
                folder = Path(folder_path)
                if folder.is_dir():
                    for file in folder.rglob('*'):
                        if file.is_file():
                            arcname = file.relative_to(folder.parent)
                            zipf.write(file, arcname)

    return output_path


def extract_zip(zip_path: str, output_dir: str) -> str:
    """
    Extract a ZIP archive to a directory.

    Args:
        zip_path: Path to the ZIP file
        output_dir: Directory to extract to

    Returns:
        Path to the extraction directory
    """
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zipf:
        zipf.extractall(output)

    return str(output)


def list_zip_contents(zip_path: str) -> List[str]:
    """
    List contents of a ZIP archive.

    Args:
        zip_path: Path to the ZIP file

    Returns:
        List of file names in the archive
    """
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        return zipf.namelist()


def main():
    import argparse

    parser = argparse.ArgumentParser(description='ZIP utility')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Create command
    create_parser = subparsers.add_parser('create', help='Create a ZIP archive')
    create_parser.add_argument('output', help='Output ZIP file path')
    create_parser.add_argument('--files', '-f', nargs='*', help='Files to include')
    create_parser.add_argument('--folders', '-d', nargs='*', help='Folders to include')

    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Extract a ZIP archive')
    extract_parser.add_argument('zip_file', help='ZIP file to extract')
    extract_parser.add_argument('output_dir', help='Output directory')

    # List command
    list_parser = subparsers.add_parser('list', help='List ZIP contents')
    list_parser.add_argument('zip_file', help='ZIP file to list')

    args = parser.parse_args()

    if args.command == 'create':
        result = create_zip(args.output, args.files, args.folders)
        print(f'Created: {result}')
    elif args.command == 'extract':
        result = extract_zip(args.zip_file, args.output_dir)
        print(f'Extracted to: {result}')
    elif args.command == 'list':
        contents = list_zip_contents(args.zip_file)
        for item in contents:
            print(item)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
