#!/usr/bin/env python
"""Direct test of admin dashboard view logic."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db.models import Sum
from decimal import Decimal
from energy.models import ConsumptionReading
from django.db.models.functions import TruncDate

User = get_user_model()

print("\n" + "=" * 70)
print("ADMIN DASHBOARD DATA TEST")
print("=" * 70)

# Get admin
admin = User.objects.filter(role='ADMIN').first()
if not admin:
    print("ERROR: No admin found")
    exit(1)

print(f"\nAdmin: {admin.email}")

# Get residents managed by admin
residents = User.objects.filter(role='RESIDENT', managed_by=admin)
print(f"Managed residents: {residents.count()}")

if not residents.exists():
    print("No residents found for this admin")
    exit(1)

# Get all readings
readings = ConsumptionReading.objects.filter(resident__in=residents)
print(f"Total readings: {readings.count()}")

# Calculate totals
total_kwh_agg = readings.aggregate(total=Sum('consumption_kwh', output_field=Decimal))
total_kwh = total_kwh_agg['total'] or 0

total_cost_agg = readings.aggregate(total=Sum('cost_estimate', output_field=Decimal))
total_cost = total_cost_agg['total'] or 0

print(f"\n✓ Total consumption: {total_kwh} kWh")
print(f"✓ Total cost: {total_cost} DH")

# Residents data
print("\n✓ Residents data:")
residents_data = []
for resident in residents:
    resident_readings = readings.filter(resident=resident)
    resident_kwh = resident_readings.aggregate(total=Sum('consumption_kwh', output_field=Decimal))['total'] or 0
    resident_cost = resident_readings.aggregate(total=Sum('cost_estimate', output_field=Decimal))['total'] or 0
    first_reading = resident_readings.first()
    meter_id = first_reading.meter_id if first_reading else 'UNKNOWN'
    
    residents_data.append({
        'email': resident.email,
        'meter_id': meter_id,
        'total_consumption_kwh': float(resident_kwh),
        'total_cost_estimate': float(resident_cost),
    })
    
    print(f"  - {resident.email}: {resident_kwh} kWh, {resident_cost} DH")

# Consumption by day
print("\n✓ Consumption by day:")
from django.db.models import DecimalField
daily_readings = readings.annotate(
    date=TruncDate('timestamp')
).values('date').annotate(
    daily_consumption=Sum('consumption_kwh', output_field=DecimalField())
).order_by('date')

consumption_by_day_data = []
for item in daily_readings:
    consumption_by_day_data.append({
        'date': str(item['date']),
        'total_consumption_kwh': float(item['daily_consumption'] or 0),
    })
    print(f"  - {item['date']}: {item['daily_consumption']} kWh")

# Average per resident
avg_per_resident = total_kwh / residents.count() if residents.count() > 0 else 0

print(f"\n✓ Average per resident: {avg_per_resident} kWh")

# Build response like the API would
response_data = {
    'admin_email': admin.email,
    'total_residents': residents.count(),
    'total_consumption_kwh': float(total_kwh),
    'total_cost_estimate': float(total_cost),
    'average_consumption_per_resident': float(avg_per_resident),
    'residents': residents_data,
    'consumption_by_day': consumption_by_day_data,
}

print("\n" + "-" * 70)
print("Response JSON:")
print("-" * 70)
import json
print(json.dumps(response_data, indent=2, ensure_ascii=False))

print("\n" + "=" * 70)
print("✓ Test complete!")
print("=" * 70 + "\n")
