# Generated by Django 3.2.19 on 2023-06-27 14:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insuree', '0023_auto_20230610_2124'),
    ]

    operations = [
        migrations.AddField(
            model_name='herautilities',
            name='is_active',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
