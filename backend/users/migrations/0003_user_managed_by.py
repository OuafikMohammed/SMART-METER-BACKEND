# Generated migration for SmartMeter Cahier des Charges

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_foyer_alter_user_role'),
    ]

    operations = [
        # Add managed_by field to User model
        migrations.AddField(
            model_name='user',
            name='managed_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='residents',
                to=settings.AUTH_USER_MODEL,
                help_text='Admin responsable. Utilisé uniquement pour les RESIDENT'
            ),
        ),
        
        # Add index for managed_by
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['managed_by'], name='users_user_managed_idx'),
        ),
    ]
