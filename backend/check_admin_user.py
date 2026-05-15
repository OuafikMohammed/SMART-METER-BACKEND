#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
admin = User.objects.filter(username='admin').first()
if admin:
    print(f"User found: {admin.username}")
    print(f"Email: {admin.email}")
    print(f"Is active: {admin.is_active}")
    print(f"Role: {admin.role}")
    print(f"Password hash: {admin.password[:30]}...")
    
    # Test password
    print(f"\nPassword check:")
    print(f"  check_password('admin123'): {admin.check_password('admin123')}")
else:
    print("User not found")
    print(f"All users: {User.objects.count()}")
    for u in User.objects.all():
        print(f"  - {u.username} (active: {u.is_active}, role: {u.role})")
