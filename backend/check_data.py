#!/usr/bin/env python
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from django.contrib.auth import get_user_model
from energy.models import Foyer, Consommation, Anomalie

User = get_user_model()

print("=== FOYERS ===")
print(f"Total: {Foyer.objects.count()}")
for foyer in Foyer.objects.all():
    print(f"  {foyer.numero_foyer} | {foyer.adresse} | {foyer.ville}")

print("\n=== RESIDENTS & ADMINS ===")
for admin in User.objects.filter(role='ADMIN'):
    residents = User.objects.filter(managed_by=admin, role='RESIDENT')
    print(f"\nAdmin: {admin.email} ({residents.count()} residents)")
    for res in residents:
        foyer_num = res.foyer.numero_foyer if res.foyer else 'NONE'
        consumptions = Consommation.objects.filter(foyer=res.foyer).count() if res.foyer else 0
        anomalies = Anomalie.objects.filter(consommation__foyer=res.foyer).count() if res.foyer else 0
        print(f"  [OK] {res.email:35} | Foyer: {foyer_num:12} | Consumptions: {consumptions:3} | Anomalies: {anomalies:3}")

print("\n=== CONSUMPTIONS ===")
print(f"Total: {Consommation.objects.count()}")
consumption_by_foyer = Consommation.objects.values('foyer__numero_foyer').count()
print(f"Foyers with data: {consumption_by_foyer}")

print("\n=== ANOMALIES ===")
total_anomalies = Anomalie.objects.count()
print(f"Total: {total_anomalies}")
if total_anomalies == 0:
    print("  [WARN] NO ANOMALIES FOUND - Need to create sample data")
else:
    anomalies_by_severity = Anomalie.objects.values('severite').count()
    print(f"  Severities: {anomalies_by_severity}")
