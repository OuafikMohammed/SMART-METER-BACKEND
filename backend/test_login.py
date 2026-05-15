#!/usr/bin/env python
"""Test login endpoint."""
import os
import django
import requests
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Get admin user and set password
admin = User.objects.filter(role='ADMIN').first()
if admin:
    print(f"Admin username: {admin.username}")
    print(f"Admin email: {admin.email}")
    admin.set_password('test123')
    admin.save()
    print("✓ Password set to: test123")
else:
    print("✗ No admin user found")
    exit(1)

# Test login endpoint
print("\n" + "="*50)
print("Testing login endpoint...")
print("="*50)

url = "http://localhost:8000/api/auth/login/"
payload = {
    "username": admin.username,
    "password": "test123"
}

print(f"\nPOST {url}")
print(f"Body: {json.dumps(payload)}")

try:
    response = requests.post(url, json=payload, timeout=5)
    print(f"\nStatus: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"\nRaw Content:\n{response.text[:500]}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✓ Success! Response fields: {list(data.keys())}")
        if 'user' in data:
            print(f"  User data: {data['user']}")
    else:
        print(f"\n✗ Error response")
        try:
            data = response.json()
            print(f"  JSON: {data}")
        except:
            print(f"  Cannot parse JSON - likely HTML error page")
            
except Exception as e:
    print(f"✗ Exception: {e}")
