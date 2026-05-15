#!/usr/bin/env python
import os
import sys
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import get_user_model
from energy.models import ConsumptionReading, Foyer, Consommation
from django.db.models import Sum, DecimalField
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

# Get admin user
admin = User.objects.filter(role='ADMIN').first()
print(f"Admin: {admin}")
print(f"Admin email: {admin.email if admin else 'None'}")

if admin:
    print(f"\n--- Checking admin data ---")
    
    # Check managed_by relationship
    residents = User.objects.filter(role='RESIDENT', managed_by=admin)
    print(f"Residents managed by admin (via managed_by): {residents.count()}")
    for r in residents[:3]:
        print(f"  - {r.email}")
    
    # Check all ConsumptionReading
    readings = ConsumptionReading.objects.all()
    print(f"\nTotal ConsumptionReading records: {readings.count()}")
    
    # Check Consommation records
    consommation = Consommation.objects.all()
    print(f"Total Consommation records: {consommation.count()}")
    
    # Check if admin has foyers
    foyers = Foyer.objects.all()
    print(f"\nTotal Foyer records: {foyers.count()}")
    for f in foyers[:3]:
        print(f"  - {f.numero_foyer}: resident_id={f.resident_id}, resident_email={f.resident.email if f.resident else 'None'}")
    
    # Check residents that have consumption data
    print(f"\n--- Residents with consumption data ---")
    residents_with_data = User.objects.filter(role='RESIDENT').filter(
        id__in=ConsumptionReading.objects.values_list('resident_id', flat=True).distinct()
    )
    print(f"Residents with ConsumptionReading: {residents_with_data.count()}")
    
    # Check admin's dashboard data
    print(f"\n--- Testing dashboard calculation ---")
    residents = User.objects.filter(role='RESIDENT', managed_by=admin)
    readings = ConsumptionReading.objects.filter(resident__in=residents)
    
    total_kwh = readings.aggregate(
        total=Sum('consumption_kwh', output_field=DecimalField())
    )['total'] or 0
    
    total_cost = readings.aggregate(
        total=Sum('cost_estimate', output_field=DecimalField())
    )['total'] or 0
    
    print(f"Admin managed residents: {residents.count()}")
    print(f"Total readings: {readings.count()}")
    print(f"Total kWh: {total_kwh}")
    print(f"Total cost: {total_cost}")
