"""
Management command pour traiter les anomalies détectées.
RG10: Commande à exécuter manuellement ou par cron.
"""
from django.core.management.base import BaseCommand
from energy.services.anomaly_service import traiter_nouvelles_anomalies


class Command(BaseCommand):
    help = "Traite les anomalies détectées depuis le dataset (anomaly_label=1)"
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.HTTP_INFO("Démarrage du traitement des anomalies..."))
        
        try:
            results = traiter_nouvelles_anomalies()
            
            # Afficher les résultats
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✓ Traitement terminé!\n"
                    f"  - Anomalies créées: {results['created']}\n"
                    f"  - Erreurs: {results['errors']}"
                )
            )
            
            if results['failed_anomalies']:
                self.stdout.write(self.style.WARNING(f"\n⚠ Anomalies en erreur:"))
                for failed in results['failed_anomalies']:
                    self.stdout.write(
                        f"  - Consommation {failed['consommation_id']}: {failed['error']}"
                    )
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"\n✗ Erreur lors du traitement: {e}")
            )
