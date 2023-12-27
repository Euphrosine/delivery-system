# Generated by Django 5.0 on 2023-12-15 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_name', models.CharField(max_length=255)),
                ('contact_number', models.CharField(max_length=15)),
                ('delivery_address', models.TextField()),
                ('items', models.TextField()),
                ('pickup_location', models.CharField(max_length=255)),
                ('pickup_contact', models.CharField(max_length=15)),
                ('delivery_date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='DeliverySentForm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transporter_name', models.CharField(max_length=255)),
                ('transporter_contact', models.CharField(max_length=15)),
                ('product_description', models.TextField()),
                ('customer_name', models.CharField(max_length=255)),
                ('customer_contact', models.CharField(max_length=15)),
                ('customer_email', models.EmailField(max_length=254)),
                ('delivery_address', models.TextField()),
                ('delivery_date', models.DateField()),
            ],
        ),
    ]
