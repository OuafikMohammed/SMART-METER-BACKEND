# Generated migration for Sprint 3: Anomalies and Alerts

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('energy', '0003_alter_consommation_anomaly_label_and_more'),
    ]

    operations = [
        # Add consultee_at and acquittee_at to Anomalie
        migrations.AddField(
            model_name='anomalie',
            name='consultee_at',
            field=models.DateTimeField(blank=True, help_text='Moment du passage en CONSULTEE', null=True),
        ),
        migrations.AddField(
            model_name='anomalie',
            name='acquittee_at',
            field=models.DateTimeField(blank=True, help_text='Moment du passage en ACQUITTEE', null=True),
        ),
        # Update Anomalie statut field with db_index
        migrations.AlterField(
            model_name='anomalie',
            name='statut',
            field=models.CharField(
                choices=[
                    ('NOUVELLE', 'Nouvelle'),
                    ('CONSULTEE', 'Consultee'),
                    ('ACQUITTEE', 'Acquittee'),
                ],
                db_index=True,
                default='NOUVELLE',
                help_text='Statut anomalie : NOUVELLE → CONSULTEE → ACQUITTEE',
                max_length=20,
            ),
        ),
        # Add statut to Alerte and update consultee_at, acquittee_at
        migrations.AddField(
            model_name='alerte',
            name='statut',
            field=models.CharField(
                choices=[
                    ('NOUVELLE', 'Nouvelle'),
                    ('CONSULTEE', 'Consultée'),
                    ('ACQUITTEE', 'Acquittée'),
                ],
                db_index=True,
                default='NOUVELLE',
                help_text='Statut alerte pour admin',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='alerte',
            name='consultee_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='alerte',
            name='acquittee_at',
            field=models.DateTimeField(blank=True, help_text="Moment de l'acquittement", null=True),
        ),
        # Update indexes
        migrations.AddIndex(
            model_name='anomalie',
            index=models.Index(fields=['consommation', 'statut'], name='energy_anom_consumm_statut_idx'),
        ),
        migrations.AddIndex(
            model_name='alerte',
            index=models.Index(fields=['statut', '-created_at'], name='energy_alrt_statut_created_idx'),
        ),
        migrations.AddIndex(
            model_name='alerte',
            index=models.Index(fields=['anomalie', 'statut'], name='energy_alrt_anomal_statut_idx'),
        ),
    ]
