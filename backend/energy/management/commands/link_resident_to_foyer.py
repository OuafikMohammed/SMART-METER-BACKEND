from django.core.management.base import BaseCommand
from users.models import User
from energy.models import Foyer

class Command(BaseCommand):
    help = 'Link resident user to a foyer'

    def handle(self, *args, **options):
        try:
            # Get or create foyer
            foyer, created = Foyer.objects.get_or_create(
                numero_foyer='FOYER-001',
                defaults={
                    'adresse': '123 Rue de Paris, 75000 Paris',
                    'code_postal': '75000',
                    'ville': 'Paris',
                    'puissance_souscrite': 6.0,
                    'is_active': True
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Foyer created: {foyer.adresse}"))
            else:
                self.stdout.write(self.style.WARNING(f"Foyer already exists: {foyer.adresse}"))

            # Update resident1 user with foyer
            resident = User.objects.get(username='resident1')
            resident.foyer = foyer
            resident.save()

            self.stdout.write(self.style.SUCCESS(f"User 'resident1' linked to foyer!"))
            self.stdout.write(self.style.SUCCESS(f"Foyer ID: {resident.foyer.id}"))
            
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("User 'resident1' not found! Create it first."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
