# Python Tools

Collection of Python utilities.

## Installation

```bash
pip install -e .
```

## Tools

### Zipper

ZIP utility for packing and unpacking files.

```bash
# Create ZIP
zipper create archiv.zip -f file1.txt file2.txt -d folder/

# Extract ZIP
zipper extract archiv.zip ./output/

# List contents
zipper list archiv.zip
```
