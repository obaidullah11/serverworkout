# Generated by Django 5.0 on 2024-10-15 18:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('train', '0029_exercise_instructions'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='session',
            name='trainer',
        ),
        migrations.AlterField(
            model_name='set',
            name='setnum',
            field=models.IntegerField(verbose_name='Set'),
        ),
    ]
