from django.core.management.base import BaseCommand
from users.models import User
from energy.models import Foyer

class Command(BaseCommand):
    help = 'Create test resident users'

    def handle(self, *args, **options):
        # Create a resident user
        try:
            resident = User.objects.create_user(
                username='resident1',
                email='resident1@smartmeter.fr',
                password='resident123',
                role='RESIDENT',
                first_name='Jean',
                last_name='Dupont'
            )

            # Create a foyer for this resident
            foyer = Foyer.objects.create(
                numero_foyer='FOYER-001',
                adresse='123 Rue de Paris, 75000 Paris',
                code_postal='75000',
                ville='Paris',
                puissance_souscrite=6.0,
                is_active=True
            )
            # Update resident with foyer
            resident.foyer = foyer
            resident.save()

            self.stdout.write(self.style.SUCCESS(f"User '{resident.username}' created successfully!"))
            self.stdout.write(self.style.SUCCESS(f"Foyer created: {foyer.adresse}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
