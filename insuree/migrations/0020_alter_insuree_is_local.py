# Generated by Django 3.2.19 on 2023-06-10 08:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insuree', '0019_alter_insuree_is_local'),
    ]

    operations = [
        migrations.AlterField(
            model_name='insuree',
            name='is_local',
            field=models.CharField(blank=True, db_column='IsLocal', max_length=100, null=True),
        ),
    ]
