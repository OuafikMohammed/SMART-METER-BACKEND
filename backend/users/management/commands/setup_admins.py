from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Crée les administrateurs spécifiés dans le PRD'

    def handle(self, *args, **options):
        admins = [
            {
                'email': 'abdelwadoudomrachi@gmail.com',
                'username': 'abdelwadoud',
                'password': '12345',
                'first_name': 'Abdel Wadoud',
                'last_name': 'Omrachi'
            },
            {
                'email': 'mohammedouafik999@gmail.com',
                'username': 'ouafik',
                'password': '12345',
                'first_name': 'Mohammed',
                'last_name': 'Ouafik'
            }
        ]

        for admin_data in admins:
            user, created = User.objects.get_or_create(
                email=admin_data['email'],
                defaults={
                    'username': admin_data['username'],
                    'first_name': admin_data['first_name'],
                    'last_name': admin_data['last_name'],
                    'role': 'ADMIN',
                    'is_staff': True,
                    'is_superuser': True
                }
            )
            
            if created or not user.check_password(admin_data['password']):
                user.set_password(admin_data['password'])
                user.save()
                status = "créé" if created else "mis à jour (password)"
                self.stdout.write(self.style.SUCCESS(f"Admin {admin_data['email']} {status}"))
            else:
                self.stdout.write(self.style.WARNING(f"Admin {admin_data['email']} existe déjà"))
