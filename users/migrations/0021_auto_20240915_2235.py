# Generated by Django 3.2.10 on 2024-09-15 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0020_user_trade_radius'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='origin',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='uid',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]