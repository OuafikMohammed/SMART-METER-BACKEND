#!/usr/bin/env python
"""
Load data from JSON into MySQL database.
"""
import os
import sys
import json
import django
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

# Configure MySQL
os.environ['DB_ENGINE'] = 'django.db.backends.mysql'
os.environ['DB_NAME'] = 'smartmeter_db'
os.environ['DB_USER'] = 'root'
os.environ['DB_PASSWORD'] = ''
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_PORT'] = '3306'

django.setup()

from django.core import management
from io import StringIO

print("📥 Loading data into MySQL...")

# Read the exported data
data_file = Path(__file__).parent / 'data_export.json'

if not data_file.exists():
    print(f"❌ File not found: {data_file}")
    sys.exit(1)

print(f"📂 Reading {data_file.name}...")
with open(data_file, 'r', encoding='utf-8') as f:
    data = json.load(f)
    
print(f"✅ Loaded {len(data)} objects from JSON")

# Load using Django's loaddata command via fixture loading
print("\n🔄 Loading into MySQL database...")

try:
    # Use StringIO to pass the JSON data directly
    from django.core.serializers import deserialize
    from django.db import transaction
    
    with open(data_file, 'r', encoding='utf-8') as f:
        fixture_data = f.read()
    
    # Load the fixture
    with transaction.atomic():
        for obj in deserialize('json', fixture_data):
            obj.save()
    
    print("✅ Data loaded successfully!")
    
except Exception as e:
    print(f"❌ Error during load: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Verify
print("\n📊 Verifying data...")
from users.models import User
from energy.models import Foyer, Consommation, Anomalie, Alerte

users = User.objects.count()
foyers = Foyer.objects.count()
consommations = Consommation.objects.count()
anomalies = Anomalie.objects.count()
alertes = Alerte.objects.count()

print(f"  Users: {users}")
print(f"  Foyers: {foyers}")
print(f"  Consommations: {consommations}")
print(f"  Anomalies: {anomalies}")
print(f"  Alertes: {alertes}")

print(f"\n✅ Migration complete! Total records: {users + foyers + consommations + anomalies + alertes}")
