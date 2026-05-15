#!/usr/bin/env python
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate, get_user_model

User = get_user_model()

# Test 1: Check if authenticate works
print("=== Test 1: Django authenticate ===")
user = authenticate(username='admin', password='admin123')
print(f"authenticate('admin', 'admin123'): {user}")

if user:
    print(f"  User ID: {user.id}")
    print(f"  Username: {user.username}")
    print(f"  Is active: {user.is_active}")
    print(f"  Role: {user.role}")

# Test 2: Manual TokenObtainPairSerializer test
print("\n=== Test 2: TokenObtainPairSerializer ===")
serializer = TokenObtainPairSerializer(data={'username': 'admin', 'password': 'admin123'})
if serializer.is_valid():
    print("✓ Serializer is valid")
    print(f"  Access token: {serializer.validated_data['access'][:30]}...")
    print(f"  Refresh token: {serializer.validated_data['refresh'][:30]}...")
else:
    print("✗ Serializer validation failed")
    print(f"  Errors: {serializer.errors}")
