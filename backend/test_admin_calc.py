#!/usr/bin/env python
import os
import sys
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import get_user_model
from energy.models import ConsumptionReading, Foyer, Consommation, Alerte
from django.db.models import Sum, DecimalField, Q
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import TruncDate

User = get_user_model()
TARIF_KWH = 2.5

# Get admin user
admin = User.objects.filter(role='ADMIN').first()
print(f"Testing admin dashboard calculation...")
print(f"Admin: {admin.email}")

# Récupérer les résidents gérés par cet admin
residents = User.objects.filter(
    role='RESIDENT',
    managed_by=admin
)

print(f"Residents managed: {residents.count()}")

# Récupérer les foyers des résidents gérés
foyers = Foyer.objects.filter(utilisateurs__in=residents).distinct()

print(f"Foyers found: {foyers.count()}")
for f in foyers[:3]:
    print(f"  - {f.numero_foyer}")

# Récupérer toutes les consommations des foyers
consommations = Consommation.objects.filter(foyer__in=foyers).order_by('-timestamp')

print(f"Consommation records: {consommations.count()}")

# Calculer les totaux
total_kwh = consommations.aggregate(
    total=Sum('kwh')
)['total'] or 0
total_kwh = float(total_kwh)

total_cost = round(total_kwh * TARIF_KWH, 2)

print(f"\nDashboard Stats:")
print(f"  Total kWh: {total_kwh}")
print(f"  Total cost: {total_cost}")
print(f"  Average per resident: {round(total_kwh / residents.count() if residents.count() > 0 else 0, 2)}")

# Données par résident (foyer)
residents_data = []
for foyer in foyers[:3]:
    foyer_consommations = consommations.filter(foyer=foyer)
    foyer_kwh = foyer_consommations.aggregate(total=Sum('kwh'))['total'] or 0
    foyer_kwh = float(foyer_kwh)
    foyer_cost = round(foyer_kwh * TARIF_KWH, 2)
    
    print(f"\nFoyer {foyer.numero_foyer}:")
    print(f"  kWh: {foyer_kwh}")
    print(f"  Cost: {foyer_cost}")

# Consommation par jour
daily_consommations = consommations.annotate(
    date=TruncDate('timestamp')
).values('date').annotate(
    daily_consumption=Sum('kwh')
).order_by('-date')[:7]

print(f"\nDaily consumption (last 7 days):")
for item in daily_consommations:
    print(f"  {item['date']}: {float(item['daily_consumption'] or 0):.2f} kWh")
