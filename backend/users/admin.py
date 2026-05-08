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
        ('SmartMeter', {'fields': ('role', 'foyer')}),
        ('Dates importantes', {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('username', 'email', 'role', 'foyer', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'foyer')
    search_fields = ('username', 'email', 'first_name', 'last_name')
