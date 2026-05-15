#!/usr/bin/env python
"""Quick database state check."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import get_user_model
from energy.models import Foyer, Consommation, Anomalie, Alerte
from django.db.models import Count, Sum

User = get_user_model()

print("DATABASE SUMMARY")
print(f"Foyers: {Foyer.objects.count()}")
print(f"Consommations: {Consommation.objects.count()}")
print(f"Anomalies: {Anomalie.objects.count()}")
print(f"Alerts: {Alerte.objects.count()}")

# Show anomaly distribution
print("\nAnomalies by status:")
for status in ['NOUVELLE', 'CONSULTEE', 'ACQUITTEE']:
    count = Anomalie.objects.filter(statut=status).count()
    print(f"  {status}: {count}")

# Show alert distribution
print("\nAlerts by status:")
for status in ['NOUVELLE', 'CONSULTEE', 'ACQUITTEE']:
    count = Alerte.objects.filter(statut=status).count()
    print(f"  {status}: {count}")

# Show consumption totals
cons = Consommation.objects.aggregate(total=Sum('kwh'))
print(f"\nTotal kWh consumed: {cons['total']:.2f if cons['total'] else 0}")
