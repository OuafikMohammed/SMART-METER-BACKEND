#!/usr/bin/env python
"""Generate comprehensive test data for SmartMeter with alerts."""
import os
import django
from datetime import datetime, timedelta
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import get_user_model
from energy.models import Foyer, Consommation, Anomalie, Alerte
from django.utils import timezone

User = get_user_model()

print("\n" + "=" * 70)
print("SMARTMETER DATA GENERATION - ALERTS & CONSUMPTION")
print("=" * 70)

# Step 1: Generate 7 days of consumption data
print("\n[STEP 1] Generating 7 days of consumption data...")
print("-" * 70)

foyers = Foyer.objects.all()
base_date = timezone.now() - timedelta(days=7)
readings_created = 0

for foyer in foyers:
    # Clear old readings from this foyer
    existing = foyer.consommations.filter(timestamp__gte=base_date)
    old_count = existing.count()
    
    if old_count > 0:
        print(f"  → Clearing {old_count} old readings for {foyer.numero_foyer}")
        existing.delete()
    
    # Generate 7 days of hourly data
    anomalies_to_create = []
    for day_offset in range(7):
        current_date = base_date + timedelta(days=day_offset)
        
        for hour in range(24):
            timestamp = current_date.replace(hour=hour, minute=0, second=0, microsecond=0)
            
            # Base consumption pattern (higher at night and evening)
            if 6 <= hour < 9:  # Morning peak
                base_kwh = 0.6
            elif 9 <= hour < 17:  # Day
                base_kwh = 0.3
            elif 17 <= hour < 22:  # Evening peak
                base_kwh = 1.0
            else:  # Night
                base_kwh = 0.2
            
            # Add variation
            variation = random.uniform(0.8, 1.3)
            kwh = base_kwh * variation
            
            # Create anomalies randomly (5% chance per reading)
            anomaly_label = None
            if random.random() < 0.05:
                anomaly_types = ['pic_consommation', 'anomalie_detectee', 'surconsommation']
                anomaly_label = random.choice(anomaly_types)
            
            consumption = Consommation.objects.create(
                foyer=foyer,
                timestamp=timestamp,
                kwh=kwh,
                anomaly_label=anomaly_label,
                temperature=20 + random.uniform(-5, 10)
            )
            
            # Flag for anomaly creation
            if anomaly_label:
                anomalies_to_create.append((consumption, anomaly_label))
            
            readings_created += 1
    
    # Create anomalies for flagged consumptions
    for consumption, anomaly_label in anomalies_to_create:
        score = random.uniform(0.6, 0.99)
        severite_choices = ['BASSE', 'MOYENNE', 'HAUTE', 'CRITIQUE']
        # Higher anomaly labels get higher severity
        if score > 0.85:
            severite = 'CRITIQUE'
        elif score > 0.75:
            severite = 'HAUTE'
        elif score > 0.65:
            severite = 'MOYENNE'
        else:
            severite = 'BASSE'
        
        Anomalie.objects.create(
            consommation=consumption,
            score_confiance=score,
            severite=severite,
            statut='NOUVELLE',
            description=f"Detected: {anomaly_label}"
        )
    
    print(f"  ✓ Created {24*7} readings for {foyer.numero_foyer} ({len(anomalies_to_create)} anomalies)")

print(f"\n✓ Total readings created: {readings_created}")

# Step 2: Create Alerts from all NOUVELLE Anomalies
print("\n[STEP 2] Creating Alerts from Anomalies...")
print("-" * 70)

# Get all anomalies that don't have alerts yet
anomalies_without_alerts = Anomalie.objects.filter(alerte__isnull=True)
alerts_created = 0

for anomalie in anomalies_without_alerts:
    alert = Alerte.objects.create(
        anomalie=anomalie,
        statut='NOUVELLE',
        acquittee=False
    )
    alerts_created += 1

print(f"✓ Created {alerts_created} alerts")

# Step 3: Verify the data
print("\n[STEP 3] Verifying Data...")
print("-" * 70)

from django.db.models import Sum, Count, Avg, Q

total_readings = Consommation.objects.count()
total_foyers = Foyer.objects.count()
avg_readings_per_foyer = total_readings / total_foyers if total_foyers > 0 else 0

# Consumption stats
cons_stats = Consommation.objects.aggregate(
    total_kwh=Sum('kwh'),
    avg_kwh=Avg('kwh'),
    with_anomalies=Count('id', filter=Q(anomaly_label__isnull=False))
)

# Anomalies stats
anomalies_stats = Anomalie.objects.values('statut').annotate(count=Count('id'))
anomalies_by_severite = Anomalie.objects.values('severite').annotate(count=Count('id'))

# Alerts stats
alerts_stats = Alerte.objects.values('statut').annotate(count=Count('id'))

print(f"\n📊 CONSUMPTION DATA:")
print(f"  - Total readings: {total_readings}")
print(f"  - Foyers with data: {total_foyers}")
print(f"  - Avg readings/foyer: {avg_readings_per_foyer:.1f}")
print(f"  - Total kWh: {cons_stats['total_kwh']:.2f}")
print(f"  - Avg kWh/reading: {cons_stats['avg_kwh']:.4f}")
print(f"  - Readings with anomalies: {cons_stats['with_anomalies']}")

print(f"\n🚨 ANOMALIES:")
for stat in anomalies_stats:
    print(f"  - {stat['statut']}: {stat['count']}")

print(f"\n  Severity distribution:")
for stat in anomalies_by_severite:
    print(f"  - {stat['severite']}: {stat['count']}")

print(f"\n🔔 ALERTS:")
alerts_total = Alerte.objects.count()
print(f"  - Total alerts: {alerts_total}")
for stat in alerts_stats:
    print(f"  - {stat['statut']}: {stat['count']}")

print(f"\n👥 USERS:")
print(f"  - Admins: {User.objects.filter(role='ADMIN').count()}")
print(f"  - Residents: {User.objects.filter(role='RESIDENT').count()}")

print("\n" + "=" * 70)
print("✓ DATA GENERATION COMPLETE!")
print("=" * 70 + "\n")
