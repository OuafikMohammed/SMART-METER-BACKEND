"""Users admin configuration."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informations personnelles', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('SmartMeter - Rôles et Relations', {'fields': ('role', 'foyer', 'managed_by')}),
        ('Dates importantes', {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('email', 'role', 'managed_by_email', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    def managed_by_email(self, obj):
        """Afficher l'email de l'admin responsable."""
        return obj.managed_by.email if obj.managed_by else '-'
    managed_by_email.short_description = 'Géré par (Admin)'

