"""
Verification script for SmartMeter seed data.
Validates all data was created correctly.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import get_user_model
from energy.models import Foyer, Consommation, Anomalie, Alerte

User = get_user_model()

print("=" * 60)
print("SMARTMETER DATA VERIFICATION")
print("=" * 60)

# Count users
total_users = User.objects.count()
admins = User.objects.filter(role='ADMIN').count()
residents = User.objects.filter(role='RESIDENT').count()

print(f"\nUSERS:")
print(f"  Total users: {total_users}")
print(f"  - Admins: {admins}")
print(f"  - Residents: {residents}")

# List users
print(f"\n  Admin Accounts:")
for admin in User.objects.filter(role='ADMIN'):
    print(f"    - {admin.email} ({admin.get_full_name()})")

print(f"\n  Resident Accounts:")
for resident in User.objects.filter(role='RESIDENT'):
    admin_info = f"managed by {resident.managed_by.email}" if resident.managed_by else "NO ADMIN ASSIGNED"
    print(f"    - {resident.email} ({admin_info})")

# Count foyers
foyers = Foyer.objects.all()
print(f"\nFOYERS: {foyers.count()}")
for foyer in foyers:
    print(f"  - {foyer.numero_foyer}: {foyer.adresse} ({foyer.puissance_souscrite} kW)")

# Count consumptions
consumptions = Consommation.objects.all()
print(f"\nCONSUMPTIONS: {consumptions.count()}")
for foyer in foyers:
    count = Consommation.objects.filter(foyer=foyer).count()
    print(f"  - {foyer.numero_foyer}: {count} readings")

# Count anomalies
anomalies = Anomalie.objects.all()
print(f"\nANOMALIES: {anomalies.count()}")
for foyer in foyers:
    count = Anomalie.objects.filter(consommation__foyer=foyer).count()
    print(f"  - {foyer.numero_foyer}: {count} anomalies")

# Count alerts
alerts = Alerte.objects.all()
print(f"\nALERTS: {alerts.count()}")

print("\n" + "=" * 60)
print("Data verification complete!")
print("=" * 60)

# Summary
print(f"\nSUMMARY:")
print(f"  Users: {total_users} ({admins} admins, {residents} residents)")
print(f"  Foyers: {foyers.count()}")
print(f"  Consumptions: {consumptions.count()}")
print(f"  Anomalies: {anomalies.count()}")
print(f"  Alerts: {alerts.count()}")
