#!/usr/bin/env python
"""Generate test tokens and verify API responses."""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APIClient

User = get_user_model()

print("\n" + "=" * 70)
print("AUTHENTICATION & API TEST")
print("=" * 70)

# Get admin and resident users
admin = User.objects.filter(role='ADMIN').first()
residents = User.objects.filter(role='RESIDENT')[:2]

if not admin:
    print("ERROR: No admin user found!")
    exit(1)

# Generate tokens
print(f"\n1. Admin User: {admin.email}")
admin_refresh = RefreshToken.for_user(admin)
admin_access = str(admin_refresh.access_token)
print(f"   Access token: {admin_access[:40]}...")

print(f"\n2. Resident Users:")
for resident in residents:
    res_refresh = RefreshToken.for_user(resident)
    res_access = str(res_refresh.access_token)
    print(f"   - {resident.email}")
    print(f"     Access token: {res_access[:40]}...")

# Test API endpoints with client
client = APIClient()

print("\n" + "-" * 70)
print("3. Testing Admin Dashboard Endpoint")
print("-" * 70)

client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_access}')

try:
    # Force populate the URL patterns
    from django.urls import get_resolver
    resolver = get_resolver()
    
    response = client.get('/api/energy/admin/dashboard/')
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n✓ Response received:")
        print(f"  - Total residents: {data.get('total_residents')}")
        print(f"  - Total consumption (kWh): {data.get('total_consumption_kwh')}")
        print(f"  - Total cost (DH): {data.get('total_cost_estimate')}")
        print(f"  - Avg consumption/resident: {data.get('average_consumption_per_resident')}")
        print(f"  - Days with data: {len(data.get('consumption_by_day', []))}")
        
        if data.get('residents'):
            print(f"\n  Residents data:")
            for res in data.get('residents', [])[:3]:
                print(f"    - {res.get('email')}: {res.get('total_consumption_kwh')} kWh")
                
        if data.get('consumption_by_day'):
            print(f"\n  Last 3 days of consumption:")
            for day in data.get('consumption_by_day', [])[-3:]:
                print(f"    - {day.get('date')}: {day.get('total_consumption_kwh')} kWh")
    elif response.status_code == 404:
        print(f"\n⚠ Endpoint not found: {response.status_code}")
        print(f"Response: {response.json()}")
    else:
        print(f"\n✗ Error: {response.status_code}")
        print(f"Response: {response.json()}")
        
except Exception as e:
    print(f"\n✗ Exception: {str(e)}")

print("\n" + "-" * 70)
print("4. Testing Foyers Endpoint")
print("-" * 70)

try:
    response = client.get('/api/energy/foyers/')
    print(f"\nStatus: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        results = data.get('results', data if isinstance(data, list) else [])
        print(f"✓ {len(results)} foyers found")
    else:
        print(f"✗ Error: {response.status_code}")
except Exception as e:
    print(f"✗ Exception: {str(e)}")

print("\n" + "=" * 70)
print("✓ Test complete!")
print("=" * 70 + "\n")
