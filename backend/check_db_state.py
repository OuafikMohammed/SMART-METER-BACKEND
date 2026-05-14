#!/usr/bin/env python
"""Check the current state of the database."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from energy.models import ConsumptionReading

User = get_user_model()

print("=" * 60)
print("DATABASE STATE CHECK")
print("=" * 60)

# Check admins
admins = User.objects.filter(role='ADMIN')
print(f"\nAdmin users: {admins.count()}")
for admin in admins:
    managed_residents = User.objects.filter(role='RESIDENT', managed_by=admin)
    print(f"  - {admin.email} (manages {managed_residents.count()} residents)")

# Check residents
residents = User.objects.filter(role='RESIDENT')
print(f"\nResidents: {residents.count()}")
for resident in residents[:5]:  # Show first 5
    readings = ConsumptionReading.objects.filter(resident=resident)
    print(f"  - {resident.email} (managed_by: {resident.managed_by.email if resident.managed_by else 'None'}, readings: {readings.count()})")

# Check consumption readings
total_readings = ConsumptionReading.objects.count()
print(f"\nTotal consumption readings: {total_readings}")

if total_readings > 0:
    from django.db.models import Sum, Count
    from decimal import Decimal
    
    agg = ConsumptionReading.objects.aggregate(
        total_kwh=Sum('consumption_kwh'),
        total_cost=Sum('cost_estimate'),
        unique_residents=Count('resident', distinct=True)
    )
    print(f"  - Total kWh: {agg['total_kwh']}")
    print(f"  - Total cost: {agg['total_cost']}")
    print(f"  - Unique residents: {agg['unique_residents']}")

print("\n" + "=" * 60)
