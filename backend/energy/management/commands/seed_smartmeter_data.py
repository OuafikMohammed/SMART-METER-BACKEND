"""
Commande Django pour remplir les données initiales SmartMeter.

Usage:
python manage.py seed_smartmeter_data

Cette commande crée :
- 2 admins
- 4 résidents (2 par admin)
- 4 foyers (1 per résident)
- 28 consommations (7 jours par foyer)
- 12 anomalies (3 par foyer)

Tous les utilisateurs ont le mot de passe : pass123
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from energy.models import Consommation, Anomalie, Foyer

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed initial data for SmartMeter Intelligence'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting SmartMeter data seeding...'))
        
        # Clear existing data (optional, comment out to preserve existing data)
        # User.objects.filter(role__in=['ADMIN', 'RESIDENT']).delete()
        # ConsumptionReading.objects.all().delete()
        
        admins_data = [
            {
                'email': 'houdamouttalib@gmail.com',
                'username': 'admin_houda',
                'password': 'pass123',
                'first_name': 'Houda',
                'last_name': 'Outtalib',
            },
            {
                'email': 'youneseljonhy@gmail.com',
                'username': 'admin_younes',
                'password': 'pass123',
                'first_name': 'Younes',
                'last_name': 'El Jonhy',
            },
        ]
        
        residents_data = [
            # Managed by admin1
            {
                'email': 'abdelwadoud@gmail.com',
                'username': 'resident_abdelwadoud',
                'password': 'pass123',
                'first_name': 'Abdelwadoud',
                'last_name': 'Mohammed',
                'admin_email': 'houdamouttalib@gmail.com',
                'meter_id': 'MTR-ADM1-001',
                'daily_consumptions': [8.5, 9.1, 7.8, 10.2, 8.9, 11.4, 9.7],
                'foyer': {
                    'numero_foyer': 'F-ADM1-001',
                    'adresse': '123 Rue de la Paix, Appartement 201',
                    'code_postal': '75001',
                    'ville': 'Paris',
                    'puissance_souscrite': 9.0,
                }
            },
            {
                'email': 'mohammed@gmail.com',
                'username': 'resident_mohammed',
                'password': 'pass123',
                'first_name': 'Mohammed',
                'last_name': 'Ahmed',
                'admin_email': 'houdamouttalib@gmail.com',
                'meter_id': 'MTR-ADM1-002',
                'daily_consumptions': [5.4, 6.2, 5.8, 7.1, 6.9, 8.0, 7.4],
                'foyer': {
                    'numero_foyer': 'F-ADM1-002',
                    'adresse': '456 Avenue des Champs, Appartement 305',
                    'code_postal': '75008',
                    'ville': 'Paris',
                    'puissance_souscrite': 6.0,
                }
            },
            # Managed by admin2
            {
                'email': 'abdelwadoudomrachi@gmail.com',
                'username': 'resident_abdelwadou_omrachi',
                'password': 'pass123',
                'first_name': 'Abdelwadou',
                'last_name': 'Omrachi',
                'admin_email': 'youneseljonhy@gmail.com',
                'meter_id': 'MTR-ADM2-001',
                'daily_consumptions': [12.3, 13.1, 11.7, 14.2, 13.6, 15.0, 14.4],
                'foyer': {
                    'numero_foyer': 'F-ADM2-001',
                    'adresse': '789 Rue du Commerce, Maison 42',
                    'code_postal': '92100',
                    'ville': 'Boulogne-Billancourt',
                    'puissance_souscrite': 12.0,
                }
            },
            {
                'email': 'mohammedouafik@gmail.com',
                'username': 'resident_mohammedouafik',
                'password': 'pass123',
                'first_name': 'Mohammed',
                'last_name': 'Ouafik',
                'admin_email': 'youneseljonhy@gmail.com',
                'meter_id': 'MTR-ADM2-002',
                'daily_consumptions': [4.2, 4.8, 5.1, 4.6, 5.3, 5.9, 5.5],
                'foyer': {
                    'numero_foyer': 'F-ADM2-002',
                    'adresse': '321 Boulevard Saint-Germain, Appartement 401',
                    'code_postal': '75005',
                    'ville': 'Paris',
                    'puissance_souscrite': 3.0,
                }
            },
        ]
        
        admins_created = 0
        admins_existing = 0
        
        # Create or update admins
        for admin_data in admins_data:
            admin, created = User.objects.update_or_create(
                email=admin_data['email'],
                defaults={
                    'username': admin_data['username'],
                    'first_name': admin_data['first_name'],
                    'last_name': admin_data['last_name'],
                    'role': 'ADMIN',
                    'is_staff': True,
                    'is_active': True,
                }
            )
            
            # Set password only if created or if user exists but password not set
            if created or not admin.check_password(admin_data['password']):
                admin.set_password(admin_data['password'])
                admin.save()
            
            if created:
                admins_created += 1
            else:
                admins_existing += 1
            
            self.stdout.write(self.style.SUCCESS(f'[OK] Admin: {admin.email}'))
        
        residents_created = 0
        residents_existing = 0
        consumptions_created = 0
        consumptions_existing = 0
        anomalies_created = 0
        foyers_created = 0
        foyers_existing = 0
        
        # Create or update residents and their consumptions & anomalies
        base_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        for resident_data in residents_data:
            # Get the admin
            try:
                admin = User.objects.get(email=resident_data['admin_email'], role='ADMIN')
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ Admin {resident_data["admin_email"]} not found for resident {resident_data["email"]}'
                    )
                )
                continue
            
            # Create or update foyer if provided
            foyer = None
            if 'foyer' in resident_data and resident_data['foyer']:
                foyer_data = resident_data['foyer']
                foyer, foyer_created = Foyer.objects.update_or_create(
                    numero_foyer=foyer_data['numero_foyer'],
                    defaults={
                        'adresse': foyer_data['adresse'],
                        'code_postal': foyer_data['code_postal'],
                        'ville': foyer_data['ville'],
                        'puissance_souscrite': foyer_data['puissance_souscrite'],
                        'is_active': True,
                    }
                )
                if foyer_created:
                    foyers_created += 1
                else:
                    foyers_existing += 1
            
            # Create or update resident
            resident, created = User.objects.update_or_create(
                email=resident_data['email'],
                defaults={
                    'username': resident_data['username'],
                    'first_name': resident_data['first_name'],
                    'last_name': resident_data['last_name'],
                    'role': 'RESIDENT',
                    'managed_by': admin,
                    'foyer': foyer,  # Assign foyer to resident
                    'is_active': True,
                }
            )
            
            # Set password
            if created or not resident.check_password(resident_data['password']):
                resident.set_password(resident_data['password'])
                resident.save()
            
            if created:
                residents_created += 1
            else:
                residents_existing += 1
            
            self.stdout.write(self.style.SUCCESS(f'[OK] Resident: {resident.email} (managed by {admin.email})'))
            if foyer:
                self.stdout.write(self.style.SUCCESS(f'     Foyer: {foyer.numero_foyer} - {foyer.adresse}'))
            
            # Create consumptions for 7 days (if foyer exists)
            if foyer:
                daily_consumptions = resident_data['daily_consumptions']
                anomaly_indices = [2, 4, 6]  # Days with anomalies (arbitrary)
                
                for day_idx, kwh in enumerate(daily_consumptions):
                    timestamp = base_date - timedelta(days=(len(daily_consumptions) - 1 - day_idx))
                    
                    consommation, created = Consommation.objects.update_or_create(
                        foyer=foyer,
                        timestamp=timestamp,
                        defaults={
                            'kwh': Decimal(str(kwh)),
                            'temperature': Decimal(str(20.0 + day_idx)),  # Vary temperature
                            'anomaly_label': None,  # Will be set if anomaly detected
                        }
                    )
                    
                    if created:
                        consumptions_created += 1
                    else:
                        consumptions_existing += 1
                    
                    # Create anomalies for some days
                    if day_idx in anomaly_indices:
                        severite_choices = ['BASSE', 'MOYENNE', 'HAUTE']
                        severite = severite_choices[day_idx % 3]
                        
                        anomalie, created = Anomalie.objects.update_or_create(
                            consommation=consommation,
                            defaults={
                                'score_confiance': Decimal(str(0.75 + (day_idx * 0.05))),  # 0.75 - 0.95
                                'severite': severite,
                                'statut': 'NOUVELLE',
                                'description': f'Anomalie détectée le jour {day_idx + 1}',
                            }
                        )
                        
                        if created:
                            anomalies_created += 1
        
        # Print summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('Seed completed successfully!'))
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(self.style.SUCCESS(f'Admins created: {admins_created}'))
        self.stdout.write(self.style.SUCCESS(f'Admins existing: {admins_existing}'))
        self.stdout.write(self.style.SUCCESS(f'Foyers created: {foyers_created}'))
        self.stdout.write(self.style.SUCCESS(f'Foyers existing: {foyers_existing}'))
        self.stdout.write(self.style.SUCCESS(f'Residents created: {residents_created}'))
        self.stdout.write(self.style.SUCCESS(f'Residents existing: {residents_existing}'))
        self.stdout.write(self.style.SUCCESS(f'Consumptions created: {consumptions_created}'))
        self.stdout.write(self.style.SUCCESS(f'Consumptions existing: {consumptions_existing}'))
        self.stdout.write(self.style.SUCCESS(f'Anomalies created: {anomalies_created}'))
        self.stdout.write(self.style.SUCCESS('='*50))
        
        # Print login credentials
        self.stdout.write(self.style.WARNING('\nLogin Credentials (all with password: pass123):'))
        self.stdout.write(self.style.WARNING('='*50))
        for admin_data in admins_data:
            self.stdout.write(f'Admin: {admin_data["email"]}')
        for resident_data in residents_data:
            self.stdout.write(f'Resident: {resident_data["email"]} (managed by {resident_data["admin_email"]})')
        self.stdout.write(self.style.WARNING('='*50))
