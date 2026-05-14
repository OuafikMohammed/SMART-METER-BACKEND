# Generated migration for ConsumptionReading model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('energy', '0005_rename_energy_alrt_statut_created_idx_energy_aler_statut_ccac5a_idx_and_more'),
    ]

    operations = [
        # Create ConsumptionReading model
        migrations.CreateModel(
            name='ConsumptionReading',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meter_id', models.CharField(db_index=True, help_text='Identifiant unique du compteur intelligent', max_length=50)),
                ('timestamp', models.DateTimeField(db_index=True, help_text='Moment de la mesure de consommation')),
                ('consumption_kwh', models.DecimalField(decimal_places=2, help_text='Consommation en kWh', max_digits=10)),
                ('cost_estimate', models.DecimalField(decimal_places=2, default=0, help_text='Coût estimé basé sur consommation * tarif', max_digits=10)),
                ('tariff_type', models.CharField(choices=[('standard', 'Standard'), ('peak', 'Heures pleines'), ('off_peak', 'Heures creuses')], default='standard', help_text='Type de tarification appliqué', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('resident', models.ForeignKey(help_text='Résident auquel appartient cette lecture', on_delete=django.db.models.deletion.CASCADE, related_name='consumption_readings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Lecture de consommation',
                'verbose_name_plural': 'Lectures de consommation',
                'db_table': 'energy_consumption_reading',
                'ordering': ['-timestamp'],
            },
        ),
        
        # Add indexes for ConsumptionReading
        migrations.AddIndex(
            model_name='consumptionreading',
            index=models.Index(fields=['resident', '-timestamp'], name='energy_cons_resident_timestamp_idx'),
        ),
        migrations.AddIndex(
            model_name='consumptionreading',
            index=models.Index(fields=['meter_id', '-timestamp'], name='energy_cons_meter_timestamp_idx'),
        ),
        migrations.AddIndex(
            model_name='consumptionreading',
            index=models.Index(fields=['timestamp'], name='energy_cons_timestamp_idx'),
        ),
        
        # Add unique constraint for ConsumptionReading
        migrations.AddConstraint(
            model_name='consumptionreading',
            constraint=models.UniqueConstraint(
                fields=['resident', 'meter_id', 'timestamp'],
                name='unique_reading_per_resident_meter_timestamp'
            ),
        ),
    ]
