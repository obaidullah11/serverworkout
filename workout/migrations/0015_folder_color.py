# Generated by Django 3.2 on 2024-11-20 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workout', '0014_bodypartmeasurement_coremeasurement'),
    ]

    operations = [
        migrations.AddField(
            model_name='folder',
            name='color',
            field=models.CharField(blank=True, default='#3b5999', max_length=7, null=True),
        ),
    ]
