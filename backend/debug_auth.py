#!/usr/bin/env python
"""
Debug script to understand authentication flow
"""
import os
import sys
import django

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

# Setup Django
django.setup()

from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from users.serializers import CustomTokenObtainPairSerializer

User = get_user_model()

print("=" * 60)
print("AUTHENTICATION DEBUG")
print("=" * 60)

# Step 1: Check if user exists
print("\n1. Checking if admin user exists...")
try:
    admin_user = User.objects.get(username='admin')
    print(f"   ✓ User found: {admin_user}")
    print(f"     - is_active: {admin_user.is_active}")
    print(f"     - role: {admin_user.role}")
except User.DoesNotExist:
    print("   ✗ User not found")
    exit(1)

# Step 2: Test local authenticate
print("\n2. Testing Django authenticate()...")
auth_user = authenticate(username='admin', password='admin123')
if auth_user:
    print(f"   ✓ authenticate() succeeded: {auth_user}")
else:
    print("   ✗ authenticate() failed")
    
# Step 3: Test TokenObtainPairSerializer locally
print("\n3. Testing TokenObtainPairSerializer.validate() locally...")
serializer = TokenObtainPairSerializer(data={'username': 'admin', 'password': 'admin123'})
try:
    if serializer.is_valid():
        print(f"   ✓ TokenObtainPairSerializer validated successfully")
        print(f"     - access: {serializer.validated_data['access'][:20]}...")
        print(f"     - refresh: {serializer.validated_data['refresh'][:20]}...")
    else:
        print(f"   ✗ TokenObtainPairSerializer validation failed: {serializer.errors}")
except Exception as e:
    print(f"   ✗ Exception: {e}")

# Step 4: Test CustomTokenObtainPairSerializer locally
print("\n4. Testing CustomTokenObtainPairSerializer.validate() locally...")
custom_serializer = CustomTokenObtainPairSerializer(data={'username': 'admin', 'password': 'admin123'})
try:
    if custom_serializer.is_valid():
        print(f"   ✓ CustomTokenObtainPairSerializer validated successfully")
        print(f"     - Keys in validated_data: {list(custom_serializer.validated_data.keys())}")
        if 'user' in custom_serializer.validated_data:
            print(f"     - User data: {custom_serializer.validated_data['user']}")
    else:
        print(f"   ✗ CustomTokenObtainPairSerializer validation failed: {custom_serializer.errors}")
except Exception as e:
    print(f"   ✗ Exception: {e}")
    import traceback
    traceback.print_exc()

# Step 5: Test manual token generation
print("\n5. Testing manual RefreshToken generation...")
try:
    refresh = RefreshToken.for_user(admin_user)
    print(f"   ✓ RefreshToken created successfully")
    print(f"     - refresh: {str(refresh)[:20]}...")
    print(f"     - access: {str(refresh.access_token)[:20]}...")
except Exception as e:
    print(f"   ✗ Exception: {e}")

print("\n" + "=" * 60)
print("DEBUG COMPLETE")
print("=" * 60)
