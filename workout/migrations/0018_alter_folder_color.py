# Generated by Django 3.2 on 2024-11-20 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workout', '0017_alter_folder_color'),
    ]

    operations = [
        migrations.AlterField(
            model_name='folder',
            name='color',
            field=models.CharField(default='#3b5999', max_length=7),
        ),
    ]
