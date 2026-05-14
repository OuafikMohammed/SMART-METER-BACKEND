#!/usr/bin/env python
"""Create sample data for testing the SmartMeter API."""
import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import get_user_model
from energy.models import ConsumptionReading, Foyer

User = get_user_model()

print("\n" + "=" * 70)
print("SAMPLE DATA GENERATOR FOR SMARTMETER")
print("=" * 70)

# 1. Create or get admin user
admin_email = 'houda.outaib@admin.smartmeter.local'
admin, admin_created = User.objects.get_or_create(
    email=admin_email,
    defaults={
        'username': 'admin_smartmeter',
        'first_name': 'Houda',
        'last_name': 'Outaib',
        'role': 'ADMIN',
        'is_staff': True,
        'is_superuser': True,
    }
)
if admin_created:
    admin.set_password('admin123')
    admin.save()
    print(f"\n✓ Created admin user: {admin_email}")
else:
    print(f"\n✓ Admin user already exists: {admin_email}")

# 2. Create or get residents
residents_data = [
    {
        'email': 'resident1@smartmeter.local',
        'username': 'resident_001',
        'first_name': 'Ahmed',
        'last_name': 'Boukarama',
        'meter_id': 'MTR-001',
    },
    {
        'email': 'resident2@smartmeter.local',
        'username': 'resident_002',
        'first_name': 'Fatima',
        'last_name': 'Morocco',
        'meter_id': 'MTR-002',
    },
]

residents_list = []
for res_data in residents_data:
    resident, res_created = User.objects.get_or_create(
        email=res_data['email'],
        defaults={
            'username': res_data['username'],
            'first_name': res_data['first_name'],
            'last_name': res_data['last_name'],
            'role': 'RESIDENT',
            'managed_by': admin,
        }
    )
    if res_created:
        resident.set_password('resident123')
        resident.save()
        print(f"✓ Created resident: {res_data['email']}")
    else:
        # Update managed_by if not set
        if not resident.managed_by:
            resident.managed_by = admin
            resident.save()
        print(f"✓ Resident already exists: {res_data['email']}")
    residents_list.append((resident, res_data['meter_id']))

# 3. Create or get foyer for each resident
print("\n" + "-" * 70)
print("Creating/Updating Foyers...")
print("-" * 70)

for resident, meter_id in residents_list:
    foyer_num = meter_id.replace('-', '')
    foyer, foyer_created = Foyer.objects.get_or_create(
        numero_foyer=foyer_num,
        defaults={
            'adresse': f'{meter_id} Street, Casablanca',
            'code_postal': '20000',
            'ville': 'Casablanca',
            'puissance_souscrite': 3.0,
            'is_active': True,
        }
    )
    if foyer_created:
        print(f"✓ Created foyer: {foyer_num}")
    
    # Link resident to foyer if not already linked
    if not resident.foyer:
        resident.foyer = foyer
        resident.save()
        print(f"  - Linked {resident.email} to {foyer_num}")

# 4. Generate consumption data for the last 7 days
print("\n" + "-" * 70)
print("Generating Consumption Readings...")
print("-" * 70)

base_date = datetime.now() - timedelta(days=7)
readings_created = 0

for resident, meter_id in residents_list:
    # Check if readings already exist for this resident in the last 7 days
    existing_readings = ConsumptionReading.objects.filter(
        resident=resident,
        timestamp__gte=base_date
    ).count()
    
    if existing_readings > 0:
        print(f"✓ Readings already exist for {resident.email} ({existing_readings} readings)")
        continue
    
    # Generate hourly readings for 7 days
    for day_offset in range(7):
        current_date = base_date + timedelta(days=day_offset)
        for hour in range(24):
            timestamp = current_date.replace(hour=hour, minute=0, second=0)
            
            # Vary consumption based on time of day (more consumption during evening)
            if 8 <= hour <= 12:  # Morning
                base_consumption = Decimal('0.3')
            elif 13 <= hour <= 17:  # Afternoon
                base_consumption = Decimal('0.2')
            elif 18 <= hour <= 23:  # Evening (peak)
                base_consumption = Decimal('0.8')
            else:  # Night
                base_consumption = Decimal('0.15')
            
            # Add some randomness
            import random
            variation = Decimal(random.uniform(0.8, 1.2))
            consumption_kwh = base_consumption * variation
            cost_estimate = consumption_kwh * Decimal('2.5')  # 2.5 DH per kWh
            
            ConsumptionReading.objects.create(
                resident=resident,
                meter_id=meter_id,
                timestamp=timestamp,
                consumption_kwh=consumption_kwh,
                cost_estimate=cost_estimate,
                tariff_type='standard'
            )
            readings_created += 1
    
    print(f"✓ Created {24 * 7} readings for {resident.email}")

print(f"\n✓ Total readings created: {readings_created}")

# 5. Verify the data
print("\n" + "-" * 70)
print("Data Verification")
print("-" * 70)

from django.db.models import Sum, Count, DecimalField

total_readings = ConsumptionReading.objects.count()
agg = ConsumptionReading.objects.aggregate(
    total_kwh=Sum('consumption_kwh', output_field=DecimalField()),
    total_cost=Sum('cost_estimate', output_field=DecimalField()),
    unique_residents=Count('resident', distinct=True)
)

print(f"\n✓ Total consumption readings: {total_readings}")
print(f"✓ Total kWh: {agg['total_kwh']}")
print(f"✓ Total cost estimate: {agg['total_cost']} DH")
print(f"✓ Unique residents: {agg['unique_residents']}")
print(f"✓ Residents managed by admin: {User.objects.filter(role='RESIDENT', managed_by=admin).count()}")

print("\n" + "=" * 70)
print("✓ Sample data generation complete!")
print("=" * 70 + "\n")
