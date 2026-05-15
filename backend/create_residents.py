#!/usr/bin/env python
"""
Create resident users linked to foyers and managed by admin
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import get_user_model
from energy.models import Foyer

User = get_user_model()

# Get admin user
admin = User.objects.get(username='admin')
print(f"Admin user: {admin}\n")

# Get all foyers
foyers = Foyer.objects.all()
print(f"Found {foyers.count()} foyers\n")

# Create a resident for each foyer
for i, foyer in enumerate(foyers, 1):
    username = f"resident_{i}"
    email = f"resident{i}@smartmeter.local"
    
    # Check if resident already exists
    resident, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': email,
            'first_name': f'Resident {i}',
            'last_name': f'Foyer {foyer.numero_foyer}',
            'role': 'RESIDENT',
            'foyer': foyer,
            'managed_by': admin,
            'is_active': True,
        }
    )
    
    if created:
        resident.set_password('resident123')
        resident.save()
        print(f"[+] Created {username} for foyer {foyer.numero_foyer}")
    else:
        # Update existing resident to ensure they're managed by admin
        resident.foyer = foyer
        resident.managed_by = admin
        resident.save()
        print(f"[+] Updated {username} for foyer {foyer.numero_foyer}")

print("\n" + "=" * 60)
print("VERIFICATION")
print("=" * 60)

# Verify admin can now see data
admin_managed = User.objects.filter(managed_by=admin)
print(f"\nResidents managed by admin: {admin_managed.count()}")

for resident in admin_managed:
    print(f"  - {resident.username} (foyer: {resident.foyer.numero_foyer if resident.foyer else 'None'})")

# Check accessible foyers
from energy.models import Foyer, Consommation, Anomalie
managed_foyers = Foyer.objects.filter(utilisateurs__in=admin_managed).distinct()
print(f"\nManagedfoyers: {managed_foyers.count()}")

managed_consommations = Consommation.objects.filter(foyer__in=managed_foyers)
print(f"Managed consommations: {managed_consommations.count()}")

managed_anomalies = Anomalie.objects.filter(consommation__foyer__in=managed_foyers)
print(f"Managed anomalies: {managed_anomalies.count()}")
