#!/usr/bin/env python3
"""Test add file functionality"""

from pathlib import Path
from p2p_core import FileManager

# Create test file
test_file = Path("/tmp/test_file.txt")
test_file.write_text("Test content")
print(f"Created test file: {test_file}")

# Create file manager
shared_dir = Path.home() / '.p2p_transfer' / 'shared'
fm = FileManager(shared_dir)

print(f"Shared dir: {shared_dir}")
print(f"Files before: {len(fm.shared_files)}")

# Try to add file
result = fm.add_file_to_shared(test_file)
print(f"Add result: {result}")
print(f"Files after: {len(fm.shared_files)}")

# List files
for f in fm.shared_files:
    print(f"  - {f.name} ({f.size} bytes)")

# Check if file exists in shared folder
dest = shared_dir / test_file.name
print(f"File exists in shared: {dest.exists()}")
