# Generated by Django 3.2.18 on 2023-03-23 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insuree', '0015_set_managed_to_true_in_all_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='insuree',
            name='certificate_number',
            field=models.CharField(blank=True, db_column='CertificateNumber', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='insuree',
            name='father_name',
            field=models.CharField(blank=True, db_column='FatherName', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='insuree',
            name='first_name',
            field=models.CharField(blank=True, db_column='FirstName', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='insuree',
            name='height',
            field=models.CharField(blank=True, db_column='Height', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='insuree',
            name='is_local',
            field=models.CharField(blank=True, db_column='IsLocal', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='insuree',
            name='mother_name',
            field=models.CharField(blank=True, db_column='MotherName', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='insuree',
            name='occupation',
            field=models.CharField(blank=True, db_column='Occupation', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='insuree',
            name='place_of_birth',
            field=models.CharField(blank=True, db_column='PlaceOfBirth', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='insuree',
            name='residential_alley',
            field=models.CharField(blank=True, db_column='ResidentialAlley', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='insuree',
            name='residential_district',
            field=models.CharField(blank=True, db_column='ResidentialDistrict', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='insuree',
            name='residential_house_number',
            field=models.CharField(blank=True, db_column='ResidentialHouseNumber', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='insuree',
            name='residential_province',
            field=models.CharField(blank=True, db_column='ResidentialProvince', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='insuree',
            name='residential_village',
            field=models.CharField(blank=True, db_column='ResidentialVillage', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='insuree',
            name='weight',
            field=models.CharField(blank=True, db_column='Weight', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='insuree',
            name='registration_date',
            field=models.CharField(blank=True, db_column='RegistrationDate', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='insuree',
            name='usual_residence',
            field=models.CharField(blank=True, db_column='UsualResidence', max_length=100, null=True),
        ),
    ]