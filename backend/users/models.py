"""
Modele utilisateur personnalise pour SmartMeter.
Respecte RG1 (authentification), RG2 (role unique), RG19 (passwords haches).
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Modele utilisateur personnalise heritant de AbstractUser.

    Respecte RG1 (authentification obligatoire) et RG19 (mots de passe haches).
    RG2 : Chaque utilisateur a un role unique (RESIDENT ou ADMIN).
    RG3 : L'acces est controle selon le role de l'utilisateur.
    """

    ROLE_CHOICES = [
        ('RESIDENT', 'Resident'),
        ('ADMIN', 'Administrateur'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='RESIDENT',
        help_text="Le role determine les permissions d'acces (RG2)",
    )
    foyer = models.ForeignKey(
        'energy.Foyer',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='utilisateurs',
        help_text="Foyer associe. Nullable pour les administrateurs (RG3)",
    )

    class Meta:
        db_table = 'users_user'
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['foyer']),
        ]

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
