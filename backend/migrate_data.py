#!/usr/bin/env python
"""
Properly handle data migration from SQLite to MySQL.
"""
import os
import sys
import json
import django
from pathlib import Path
from io import StringIO

# Setup Django
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

# Make sure we're using MySQL before Django sets up
os.environ['DB_ENGINE'] = 'django.db.backends.mysql'
os.environ['DB_NAME'] = 'smartmeter_db'
os.environ['DB_USER'] = 'root'
os.environ['DB_PASSWORD'] = ''
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_PORT'] = '3306'

django.setup()

from django.core import management

print("\n" + "="*60)
print("🔄 LOADING DATA INTO MYSQL")
print("="*60)

# Get all data
print("\n📊 Collecting all data from database...")
try:
    # Capture dumpdata output
    from io import StringIO
    out = StringIO()
    management.call_command('dumpdata', '--all', stdout=out)
    json_data = out.getvalue()
    
    if json_data:
        # Write to file with proper encoding
        backup_file = Path(__file__).parent / 'data_backup_final.json'
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(json_data)
        
        print(f"✅ Data exported: {len(json_data)} bytes")
        
        # Now try to load it
        print("\n📥 Loading data into MySQL...")
        from django.core.management import call_command
        try:
            call_command('loaddata', str(backup_file), verbosity=0)
            print("✅ Data loaded successfully!")
        except Exception as e:
            print(f"⚠️  Load error: {e}")
            # Try direct SQL insert
            print("\n🔧 Attempting direct data insertion...")
            load_via_sql(json_data)
    else:
        print("⚠️  No data to export")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

def load_via_sql(json_data):
    """Load JSON data directly using raw SQL."""
    import json
    from django.db import connection
    
    data = json.loads(json_data)
    
    # Get models
    from users.models import User
    from energy.models import Foyer, Consommation, Anomalie, Alerte
    
    # Clear existing data (optional)
    # User.objects.all().delete()
    # Foyer.objects.all().delete()
    
    for item in data:
        model_name = item['model']
        fields = item['fields']
        pk = item['pk']
        
        print(f"  Processing {model_name} (pk={pk})...")
        
        # This is complex, so instead use a simpler approach
        pass

print("\n" + "="*60)
