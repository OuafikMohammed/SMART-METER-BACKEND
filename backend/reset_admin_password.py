import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
admin = User.objects.filter(username='admin').first()
if admin:
    admin.set_password('test123')
    admin.save()
    print(f'Admin password reset to: test123')
    print(f'Check password: {admin.check_password("test123")}')
else:
    print('Admin not found')
