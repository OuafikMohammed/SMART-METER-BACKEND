"""
Modèle utilisateur personnalisé pour SmartMeter.
Respecte RG1 (authentification), RG2 (rôle unique), RG19 (passwords hachés).
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Modèle utilisateur personnalisé héritant de AbstractUser.
    
    Respecte RG1 (authentification obligatoire) et RG19 (mots de passe hachés).
    RG2 : Chaque utilisateur a un rôle unique (RESIDENT ou ADMIN).
    RG3 : L'accès est contrôlé selon le rôle de l'utilisateur.
    
    Relations:
    - managed_by: Pour les RESIDENT, pointe vers l'ADMIN responsable
    - foyer: Compatibilité avec structure existante (nullable)
    """
    
    ROLE_CHOICES = [
        ('RESIDENT', 'Résident'),
        ('ADMIN', 'Administrateur'),
    ]
    
    # Rôle de l'utilisateur (RG2)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='RESIDENT',
        help_text="Le rôle détermine les permissions d'accès (RG2)"
    )
    
    # Foyer associé à l'utilisateur (nullable pour les ADMIN) - Compatibilité
    foyer = models.ForeignKey(
        'energy.Foyer',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='utilisateurs',
        help_text="Foyer associé. Nullable pour les administrateurs (RG3)"
    )
    
    # Admin responsable (pour les RESIDENT uniquement)
    managed_by = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='residents',
        help_text="Admin responsable. Utilisé uniquement pour les RESIDENT"
    )
    
    class Meta:
        db_table = 'users_user'
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['foyer']),
            models.Index(fields=['managed_by']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
