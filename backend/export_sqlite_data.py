#!/usr/bin/env python
"""
Export data to JSON using Python directly (no encoding issues).
"""
import os
import sys
import json
import django
from pathlib import Path
from io import StringIO

sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

# Use SQLite for this export
os.environ['DB_ENGINE'] = 'django.db.backends.sqlite3'

django.setup()

from django.core import management

print("📊 Exporting data from SQLite...")

# Use StringIO to capture output
out = StringIO()
management.call_command('dumpdata', '--all', indent=2, stdout=out)

json_str = out.getvalue()
print(f"✅ Exported {len(json_str)} characters")

# Parse and validate
try:
    data = json.loads(json_str)
    print(f"✅ Valid JSON with {len(data)} objects")
    
    # Write to file properly
    backup_file = Path(__file__).parent / 'data_export.json'
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved to {backup_file.name} ({backup_file.stat().st_size} bytes)")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
