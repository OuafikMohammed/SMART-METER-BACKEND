#!/usr/bin/env python
"""Check the current state of the database."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import get_user_model
from energy.models import Foyer, Consommation, Anomalie, Alerte

User = get_user_model()

print("=" * 60)
print("DATABASE STATE CHECK")
print("=" * 60)

# Check users
admins = User.objects.filter(role='ADMIN')
print(f"\nAdmin users: {admins.count()}")
for admin in admins:
    print(f"  - {admin.email}")

residents = User.objects.filter(role='RESIDENT')
print(f"\nResident users: {residents.count()}")

# Check foyers
foyers = Foyer.objects.all()
print(f"\nFoyers: {foyers.count()}")
for foyer in foyers[:3]:
    cons = foyer.consommations.count()
    print(f"  - {foyer.numero_foyer}: {cons} readings")

# Check consumption
total_cons = Consommation.objects.count()
print(f"\nTotal consommations: {total_cons}")

# Check anomalies
anomalies = Anomalie.objects.all()
print(f"Anomalies: {anomalies.count()}")
print(f"  - NOUVELLE: {anomalies.filter(statut='NOUVELLE').count()}")
print(f"  - CONSULTEE: {anomalies.filter(statut='CONSULTEE').count()}")
print(f"  - ACQUITTEE: {anomalies.filter(statut='ACQUITTEE').count()}")

# Check alertes
alertes = Alerte.objects.all()
print(f"\nAlertes: {alertes.count()}")
print(f"  - NOUVELLE: {alertes.filter(statut='NOUVELLE').count()}")
print(f"  - CONSULTEE: {alertes.filter(statut='CONSULTEE').count()}")
print(f"  - ACQUITTEE: {alertes.filter(statut='ACQUITTEE').count()}")

print("\n" + "=" * 60)
