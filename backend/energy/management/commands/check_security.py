"""
Commande de gestion Django pour vérifier la sécurité du projet SmartMeter.

Vérifie:
1. RG19: Tous les passwords sont hashés (pbkdf2_sha256)
2. RG20: Journal d'audit complet (ActionLog)
3. Rapport de sécurité
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from energy.models import ActionLog

User = get_user_model()


class Command(BaseCommand):
    help = "Vérifier la sécurité du projet SmartMeter (RG19, RG20)"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("\n" + "=" * 60)
        )
        self.stdout.write(
            self.style.SUCCESS("AUDIT DE SÉCURITÉ - SMARTMETER")
        )
        self.stdout.write(
            self.style.SUCCESS("=" * 60 + "\n")
        )

        # 1. Vérifier le hashage des passwords (RG19)
        self.stdout.write(
            self.style.HTTP_INFO("1. Vérification du hashage des passwords (RG19)...")
        )
        self._check_password_hashing()

        # 2. Vérifier l'ActionLog (RG20)
        self.stdout.write(
            self.style.HTTP_INFO("\n2. Vérification du journal d'audit (RG20)...")
        )
        self._check_action_log()

        # 3. Rapport récapitulatif
        self.stdout.write(
            self.style.SUCCESS("\n" + "=" * 60)
        )
        self.stdout.write(
            self.style.SUCCESS("AUDIT COMPLÉTÉ AVEC SUCCÈS")
        )
        self.stdout.write(
            self.style.SUCCESS("=" * 60 + "\n")
        )

    def _check_password_hashing(self):
        """Vérifier que tous les passwords utilisateurs sont hashés (RG19)."""
        users = User.objects.all()
        total_users = users.count()
        secure_passwords = 0
        insecure_users = []

        for user in users:
            # Les passwords Django commencent par 'pbkdf2_sha256$' quand hashés
            if user.password and user.password.startswith('pbkdf2_sha256$'):
                secure_passwords += 1
            else:
                insecure_users.append(user.username)

        self.stdout.write(
            f"   ✓ Total utilisateurs: {total_users}"
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"   ✓ Passwords sécurisés (pbkdf2_sha256): {secure_passwords}"
            )
        )

        if insecure_users:
            self.stdout.write(
                self.style.ERROR(
                    f"   ✗ Passwords NON sécurisés: {len(insecure_users)}"
                )
            )
            for username in insecure_users:
                self.stdout.write(
                    self.style.ERROR(f"     - {username}")
                )
        else:
            self.stdout.write(
                self.style.SUCCESS("   ✓ TOUS les passwords sont sécurisés ✓")
            )

    def _check_action_log(self):
        """Vérifier le journal d'audit ActionLog (RG20)."""
        now = timezone.now()
        date_24h_ago = now - timedelta(hours=24)

        # Compter les logs des 24 dernières heures
        total_logs = ActionLog.objects.count()
        logs_24h = ActionLog.objects.filter(timestamp__gte=date_24h_ago).count()

        self.stdout.write(
            f"   ✓ Total ActionLog: {total_logs}"
        )
        self.stdout.write(
            f"   ✓ Logs (dernières 24h): {logs_24h}"
        )

        # Afficher les actions trackées
        actions = ActionLog.objects.values_list('action', flat=True).distinct()
        self.stdout.write(
            f"\n   Types d'actions trackées ({len(actions)}):"
        )
        for action in sorted(actions):
            count = ActionLog.objects.filter(action=action).count()
            self.stdout.write(f"     - {action}: {count} logs")

        # Vérifier les actions requises par RG20
        required_actions = ['LOGIN', 'CHAT_IA', 'IMPORT_CSV', 'ACQUITTER_ALERTE', 'MARQUER_ANOMALIE_ACQUITTEE']
        self.stdout.write(
            f"\n   Actions requises (RG20):"
        )
        for action in required_actions:
            count = ActionLog.objects.filter(action=action).count()
            status_icon = "✓" if count > 0 else "✗"
            self.stdout.write(f"     {status_icon} {action}: {count} logs")

        if logs_24h > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n   ✓ Journal d'audit actif et fonctionnel (RG20) ✓"
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"   ⚠ Aucun log dans les 24 dernières heures"
                )
            )
