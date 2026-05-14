#!/usr/bin/env python
"""Check database state directly."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import get_user_model
from energy.models import ConsumptionReading

User = get_user_model()

print("\n" + "=" * 70)
print("DATABASE STATE ANALYSIS")
print("=" * 70)

# All users
print("\n1. ALL USERS:")
all_users = User.objects.all()
for user in all_users:
    print(f"  ID={user.id}, {user.email}, Role={user.role}, managed_by={user.managed_by_id if user.managed_by else 'None'}")

# All consumption readings
print("\n2. ALL CONSUMPTION READINGS:")
readings = ConsumptionReading.objects.all()
print(f"Total readings: {readings.count()}")

if readings.exists():
    print("Sample readings:")
    for reading in readings[:5]:
        print(f"  Resident ID={reading.resident_id}, Meter={reading.meter_id}, kWh={reading.consumption_kwh}, Timestamp={reading.timestamp}")
    
    # Group by resident
    print("\nReadings by resident:")
    from django.db.models import Count
    residents_with_readings = readings.values('resident_id').annotate(count=Count('id')).order_by('resident_id')
    for item in residents_with_readings:
        resident = User.objects.get(id=item['resident_id'])
        print(f"  Resident ID={item['resident_id']} ({resident.email}): {item['count']} readings")

print("\n" + "=" * 70)
