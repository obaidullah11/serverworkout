# Generated by Django 5.0 on 2024-10-17 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workout', '0004_folder_workout_folder'),
    ]

    operations = [
        migrations.AddField(
            model_name='folder',
            name='device_id',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
    ]
