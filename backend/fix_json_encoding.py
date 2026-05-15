#!/usr/bin/env python
"""
Fix JSON file encoding by removing BOM.
"""
import json

# Read the problematic file
with open('sqlite_backup.json', 'rb') as f:
    raw_data = f.read()

# Check for BOM
print(f'File size: {len(raw_data)} bytes')
print(f'First 10 bytes: {raw_data[:10].hex()}')

# Fix by removing BOM if present
if raw_data.startswith(b'\xef\xbb\xbf'):  # UTF-8 BOM
    print("Removing UTF-8 BOM...")
    raw_data = raw_data[3:]
elif raw_data.startswith(b'\xff\xfe'):  # UTF-16 LE BOM
    print("Converting from UTF-16 LE...")
    raw_data = raw_data.decode('utf-16').encode('utf-8')
elif raw_data.startswith(b'\xfe\xff'):  # UTF-16 BE BOM
    print("Converting from UTF-16 BE...")
    raw_data = raw_data.decode('utf-16').encode('utf-8')

# Verify it's valid JSON
try:
    data = json.loads(raw_data.decode('utf-8'))
    print(f"✅ Valid JSON with {len(data)} objects")
except Exception as e:
    print(f"❌ JSON error: {e}")

# Write clean version
with open('sqlite_backup_clean.json', 'wb') as f:
    f.write(raw_data)

print("✅ Clean file written: sqlite_backup_clean.json")
