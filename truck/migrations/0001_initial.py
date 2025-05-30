# Generated by Django 5.0.1 on 2025-05-10 11:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AllowedGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_id', models.CharField(help_text='Group id', max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Kompaniya nomi (masalan: MUNISA)', max_length=100, unique=True)),
                ('is_active', models.BooleanField(default=True, help_text='Kompaniya hozirda faolmi?')),
            ],
        ),
        migrations.CreateModel(
            name='OrientationType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Orientation nomi (masalan: DISPATCH)', max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='TelegramUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telegram_id', models.BigIntegerField(unique=True)),
                ('first_name', models.CharField(blank=True, max_length=100, null=True)),
                ('last_name', models.CharField(blank=True, max_length=100, null=True)),
                ('username', models.CharField(blank=True, max_length=100, null=True)),
                ('language_code', models.CharField(blank=True, max_length=100, null=True)),
                ('is_bot', models.BooleanField(default=False)),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='TruckStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Holat nomi (masalan: Enroute, In Maintenance, Active)', max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Truck',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(help_text='Truck ichki raqami (masalan: TRK-245)', max_length=100, unique=True)),
                ('plate_number', models.CharField(blank=True, help_text='Davlat raqami (masalan: TX 98325 AB)', max_length=100, null=True)),
                ('vin_number', models.CharField(blank=True, help_text='VIN (Vehicle Identification Number)', max_length=100, null=True)),
                ('make', models.CharField(blank=True, max_length=100, null=True)),
                ('model', models.CharField(blank=True, max_length=100, null=True)),
                ('tm_or_b', models.CharField(blank=True, help_text='TM/B (masalan: AT, MT)', max_length=100, null=True)),
                ('color', models.CharField(blank=True, max_length=100, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('year', models.PositiveIntegerField(blank=True, null=True)),
                ('st', models.CharField(blank=True, help_text='ST (masalan: TX, IL)', max_length=100, null=True)),
                ('whose_truck', models.CharField(blank=True, help_text='Whose Truck (masalan: Owner)', max_length=100, null=True)),
                ('owner_name', models.CharField(blank=True, max_length=100, null=True)),
                ('driver_name', models.CharField(blank=True, max_length=100, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='truck.company')),
                ('status', models.ForeignKey(blank=True, help_text='Truck status (masalan: Enroute)', null=True, on_delete=django.db.models.deletion.SET_NULL, to='truck.truckstatus')),
            ],
        ),
        migrations.CreateModel(
            name='Driver',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(help_text='Haydovchining to‘liq ismi', max_length=100)),
                ('date', models.DateField(help_text='Kiritilgan sana')),
                ('mode', models.CharField(choices=[('online', 'Online'), ('offline', 'Offline')], default='offline', help_text='Driverning hozirgi holati', max_length=100)),
                ('driver_type', models.CharField(blank=True, choices=[('company', 'Company Driver'), ('owner', 'Owner Operator'), ('reefer', 'Reefer Driver')], help_text='Driver turi', max_length=100, null=True)),
                ('confirmation', models.CharField(blank=True, help_text='Confirmation status', max_length=100, null=True)),
                ('sign', models.CharField(blank=True, help_text='Sign (masalan: signed)', max_length=100, null=True)),
                ('docusign', models.CharField(blank=True, help_text='DocuSign status', max_length=100, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='truck.company')),
                ('truck', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='truck.truck')),
            ],
        ),
        migrations.CreateModel(
            name='TruckInspection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('registration', models.CharField(max_length=100)),
                ('annual_inspection', models.CharField(max_length=100)),
                ('rental_agreement', models.CharField(max_length=100)),
                ('outbound_inspection', models.CharField(max_length=100)),
                ('truck', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='inspection', to='truck.truck')),
            ],
        ),
        migrations.CreateModel(
            name='TruckInsurance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('proof_of_ownership', models.BooleanField(default=False)),
                ('safety_carrier', models.BooleanField(default=False)),
                ('liability_and_cargo', models.BooleanField(default=False)),
                ('physical_damage', models.BooleanField(default=False)),
                ('physical_exp', models.DateField(blank=True, null=True)),
                ('link', models.URLField(blank=True, null=True)),
                ('truck', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='insurance', to='truck.truck')),
            ],
        ),
        migrations.CreateModel(
            name='TruckOrientation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('not_done', 'Not Done'), ('done', 'Done')], default='not_done', help_text='Orientation holati', max_length=100)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('orientation_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='truck.orientationtype')),
                ('truck', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orientations', to='truck.truck')),
            ],
            options={
                'unique_together': {('truck', 'orientation_type')},
            },
        ),
    ]
