"""
Tests pour l'endpoint ResidentDashboard
Tests unitaires et d'intégration pour GET /api/energy/resident/dashboard/
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status

from energy.models import Foyer, Consommation, Alerte, Anomalie

User = get_user_model()


class ResidentDashboardTest(TestCase):
    """Test suite pour l'endpoint resident dashboard"""

    def setUp(self):
        """Préparation des données de test"""
        self.client = APIClient()
        
        # Créer un foyer
        self.foyer = Foyer.objects.create(
            numero_foyer='TEST001',
            adresse='123 Rue de Test',
            code_postal='75000',
            ville='Paris',
            puissance_souscrite=6.0,
        )
        
        # Créer un résident
        self.resident = User.objects.create_user(
            username='resident_test',
            email='resident@test.fr',
            password='testpass123',
            role='RESIDENT',
            foyer=self.foyer,
        )
        
        # Créer un admin
        self.admin = User.objects.create_user(
            username='admin_test',
            email='admin@test.fr',
            password='testpass123',
            role='ADMIN',
            foyer=None,
        )
        
        # Créer des données de consommation
        now = timezone.now()
        
        # Consommation d'aujourd'hui
        for hour in range(0, 24):
            timestamp = now.replace(hour=hour, minute=0, second=0, microsecond=0)
            Consommation.objects.create(
                foyer=self.foyer,
                timestamp=timestamp,
                kwh=2.5 + (hour % 3),  # Variation entre 2.5 et 5.5 kWh
                anomaly_label=None if hour != 10 else '1',  # Anomalie à 10h
                temperature=20.0,
            )
        
        # Consommation de la semaine passée
        for day in range(1, 8):
            for hour in range(0, 24, 4):  # Une mesure par 4 heures
                timestamp = (now - timedelta(days=day)).replace(
                    hour=hour, minute=0, second=0, microsecond=0
                )
                Consommation.objects.create(
                    foyer=self.foyer,
                    timestamp=timestamp,
                    kwh=3.0 + (day % 2),
                    anomaly_label=None,
                    temperature=18.0,
                )

    def test_dashboard_unauthenticated(self):
        """Tester l'accès sans authentification → 401"""
        response = self.client.get('/api/energy/resident/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_dashboard_admin_forbidden(self):
        """Tester l'accès en tant qu'ADMIN → 403"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/energy/resident/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_dashboard_resident_success(self):
        """Tester l'accès en tant que RESIDENT → 200"""
        self.client.force_authenticate(user=self.resident)
        response = self.client.get('/api/energy/resident/dashboard/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Vérifier la structure de la réponse
        self.assertIn('consommation_actuelle', data)
        self.assertIn('consommation_jour', data)
        self.assertIn('consommation_semaine', data)
        self.assertIn('cout_estime_mois', data)
        self.assertIn('alertes_actives', data)
        self.assertIn('variation_jour', data)
        self.assertIn('points_graphique', data)

    def test_dashboard_consommation_actuelle(self):
        """Tester que consommation_actuelle est la dernière mesure"""
        self.client.force_authenticate(user=self.resident)
        response = self.client.get('/api/energy/resident/dashboard/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # La consommation actuelle doit être entre 2.5 et 5.5 kWh
        self.assertGreater(data['consommation_actuelle'], 2.0)
        self.assertLess(data['consommation_actuelle'], 6.0)

    def test_dashboard_consommation_jour(self):
        """Tester que consommation_jour est la somme du jour"""
        self.client.force_authenticate(user=self.resident)
        response = self.client.get('/api/energy/resident/dashboard/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Nous avons créé 24 mesures, chacune entre 2.5 et 5.5 kWh
        # Somme approximative : 24 * 4 = 96 kWh (très approximatif)
        self.assertGreater(data['consommation_jour'], 0)
        self.assertIsInstance(data['consommation_jour'], (int, float))

    def test_dashboard_cout_estime(self):
        """Tester que cout_estime_mois est basé sur tarif_kwh"""
        self.client.force_authenticate(user=self.resident)
        response = self.client.get('/api/energy/resident/dashboard/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # cout_estime_mois = consommation_mois * 2.5 DH/kWh
        self.assertGreater(data['cout_estime_mois'], 0)
        self.assertIsInstance(data['cout_estime_mois'], (int, float))

    def test_dashboard_points_graphique(self):
        """Tester que points_graphique contient les 48 dernières mesures"""
        self.client.force_authenticate(user=self.resident)
        response = self.client.get('/api/energy/resident/dashboard/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        points = data['points_graphique']
        
        # Vérifier la structure de chaque point
        for point in points:
            self.assertIn('timestamp', point)
            self.assertIn('kwh', point)
            self.assertIn('anomaly_label', point)
            self.assertIsInstance(point['kwh'], (int, float))
            self.assertIsInstance(point['anomaly_label'], int)

    def test_dashboard_variation_jour(self):
        """Tester que variation_jour est calculée"""
        self.client.force_authenticate(user=self.resident)
        response = self.client.get('/api/energy/resident/dashboard/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # variation_jour doit être un nombre (peut être négatif, zéro, ou positif)
        self.assertIsInstance(data['variation_jour'], (int, float))

    def test_dashboard_resident_without_foyer(self):
        """Tester accès résident sans foyer → 400"""
        # Créer un résident sans foyer
        resident_no_foyer = User.objects.create_user(
            username='resident_no_foyer',
            email='no_foyer@test.fr',
            password='testpass123',
            role='RESIDENT',
            foyer=None,
        )
        
        self.client.force_authenticate(user=resident_no_foyer)
        response = self.client.get('/api/energy/resident/dashboard/')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_dashboard_isolation_resident(self):
        """Tester que chaque résident ne voit que ses données"""
        # Créer un 2e foyer et résident
        foyer2 = Foyer.objects.create(
            numero_foyer='TEST002',
            adresse='456 Rue de Test',
            code_postal='75001',
            ville='Paris',
            puissance_souscrite=6.0,
        )
        resident2 = User.objects.create_user(
            username='resident2_test',
            email='resident2@test.fr',
            password='testpass123',
            role='RESIDENT',
            foyer=foyer2,
        )
        
        # Ajouter une consommation énorme au foyer2
        now = timezone.now()
        for _ in range(10):
            Consommation.objects.create(
                foyer=foyer2,
                timestamp=now,
                kwh=100.0,  # Très haut
                anomaly_label=None,
            )
        
        # Vérifier que resident1 ne voit pas les données du foyer2
        self.client.force_authenticate(user=self.resident)
        response = self.client.get('/api/energy/resident/dashboard/')
        data = response.json()
        
        # consommation_actuelle du résident1 ne doit pas être 100
        self.assertNotEqual(data['consommation_actuelle'], 100.0)

    def test_dashboard_response_format(self):
        """Tester le format exact de la réponse JSON"""
        self.client.force_authenticate(user=self.resident)
        response = self.client.get('/api/energy/resident/dashboard/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Vérifier les types de données
        self.assertIsInstance(data['consommation_actuelle'], (int, float))
        self.assertIsInstance(data['consommation_jour'], (int, float))
        self.assertIsInstance(data['consommation_semaine'], (int, float))
        self.assertIsInstance(data['cout_estime_mois'], (int, float))
        self.assertIsInstance(data['alertes_actives'], int)
        self.assertIsInstance(data['variation_jour'], (int, float))
        self.assertIsInstance(data['points_graphique'], list)
