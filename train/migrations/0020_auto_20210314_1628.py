# Generated by Django 3.1.7 on 2021-03-14 20:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('train', '0019_remove_setgroup_kaatsu'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exercise',
            name='name',
            field=models.CharField(max_length=40, unique=True),
        ),
    ]