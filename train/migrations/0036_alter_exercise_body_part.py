# Generated by Django 5.0 on 2024-10-20 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('train', '0035_exercise_exercise_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exercise',
            name='body_part',
            field=models.CharField(max_length=225),
        ),
    ]