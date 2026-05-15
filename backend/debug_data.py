#!/usr/bin/env python
"""
Debug why admin user can't see data
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import get_user_model
from energy.models import Foyer, Consommation, Anomalie, Alerte

User = get_user_model()

# Check admin user
admin = User.objects.get(username='admin')
print(f"Admin user: {admin}")
print(f"  - foyer: {admin.foyer}")
print(f"  - managed_by: {admin.managed_by}")

# Check what foyers exist
foyers = Foyer.objects.all()
print(f"\nAll foyers: {foyers.count()}")
for foyer in foyers:
    print(f"  - {foyer.numero_foyer}: utilisateurs={foyer.utilisateurs.count()}, consommations={foyer.consommations.count()}")

# Check consommations
consommations = Consommation.objects.all()
print(f"\nAll consommations: {consommations.count()}")

# Check anomalies
anomalies = Anomalie.objects.all()
print(f"All anomalies: {anomalies.count()}")

# Check alerts
alertes = Alerte.objects.all()
print(f"All alertes: {alertes.count()}")

# Now simulate the filtering logic from energy/views.py
print("\n" + "=" * 60)
print("SIMULATING ADMIN VIEW FILTERING")
print("=" * 60)

# Get managed residents (users managed by this admin)
managed_residents = User.objects.filter(managed_by=admin)
print(f"\nManaged residents: {managed_residents.count()}")
for user in managed_residents:
    print(f"  - {user.username}")

# Get foyers of managed residents
managed_foyers = Foyer.objects.filter(utilisateurs__in=managed_residents)
print(f"\nManaged foyers: {managed_foyers.count()}")

# Get consommations of managed foyers
managed_consommations = Consommation.objects.filter(foyer__in=managed_foyers)
print(f"Managed consommations: {managed_consommations.count()}")

# Get anomalies of managed foyers
managed_anomalies = Anomalie.objects.filter(consommation__foyer__in=managed_foyers)
print(f"Managed anomalies: {managed_anomalies.count()}")
