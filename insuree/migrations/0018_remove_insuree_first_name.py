# Generated by Django 3.2.16 on 2023-05-24 13:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('insuree', '0017_add_model_hera_utilities'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='insuree',
            name='first_name',
        ),
    ]
