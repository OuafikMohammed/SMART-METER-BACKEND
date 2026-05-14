#!/usr/bin/env python
"""Test the API endpoints to ensure they work correctly."""
import os
import django
import requests
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Get admin user
admin = User.objects.filter(role='ADMIN').first()

if not admin:
    print("No admin user found!")
    exit(1)

# Get token by logging in
print("\n" + "=" * 70)
print("API ENDPOINT TEST")
print("=" * 70)

# Test endpoints
print("\n1. Testing API structure...")
print(f"   Admin user: {admin.email}")

# Get Django rest framework test client
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

# Generate token for admin
refresh = RefreshToken.for_user(admin)
access_token = str(refresh.access_token)

print(f"   Token: {access_token[:50]}...")

# Create API client
client = APIClient()
client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

# Test admin dashboard endpoint
print("\n2. Testing GET /api/energy/admin/dashboard/...")
response = client.get('/api/energy/admin/dashboard/')
print(f"   Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"   Response data:")
    print(f"     - total_residents: {data.get('total_residents')}")
    print(f"     - total_consumption_kwh: {data.get('total_consumption_kwh')}")
    print(f"     - total_cost_estimate: {data.get('total_cost_estimate')}")
    print(f"     - average_consumption_per_resident: {data.get('average_consumption_per_resident')}")
    print(f"     - consumption_by_day: {len(data.get('consumption_by_day', []))} days")
else:
    print(f"   ERROR: {response.status_code}")
    print(f"   Response: {response.content}")

# Test foyers endpoint
print("\n3. Testing GET /api/energy/foyers/...")
response = client.get('/api/energy/foyers/')
print(f"   Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"   Response: {len(data.get('results', []))} foyers found")
else:
    print(f"   ERROR: {response.status_code}")

# Test consommations endpoint
print("\n4. Testing GET /api/energy/consommations/...")
response = client.get('/api/energy/consommations/')
print(f"   Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"   Response: {len(data.get('results', []))} consommations found")
else:
    print(f"   ERROR: {response.status_code}")

print("\n" + "=" * 70)
print("✓ API endpoint test complete!")
print("=" * 70 + "\n")
