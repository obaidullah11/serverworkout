# Generated by Django 5.0 on 2024-10-17 18:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workout', '0005_folder_device_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workout',
            name='folder',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='workouts', to='workout.folder'),
        ),
    ]
