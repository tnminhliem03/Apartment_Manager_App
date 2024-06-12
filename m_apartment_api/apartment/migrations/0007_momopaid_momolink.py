# Generated by Django 5.0.4 on 2024-06-12 04:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apartment', '0006_receipt_order_id_receipt_pay_type_momopaymentlink_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='MomoPaid',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('partner_code', models.CharField(max_length=20)),
                ('order_id', models.CharField(max_length=50, unique=True)),
                ('request_id', models.CharField(max_length=50, unique=True)),
                ('amount', models.IntegerField()),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('order_info', models.CharField(max_length=255)),
                ('order_type', models.CharField(max_length=50)),
                ('trans_id', models.BigIntegerField()),
                ('pay_type', models.CharField(max_length=20)),
                ('signature', models.CharField(max_length=100)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MomoLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('partner_code', models.CharField(max_length=20)),
                ('order_id', models.CharField(max_length=50, unique=True)),
                ('request_id', models.CharField(max_length=50, unique=True)),
                ('amount', models.IntegerField()),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('pay_url', models.CharField(max_length=255)),
                ('short_link', models.CharField(max_length=255)),
                ('payment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apartment.payment')),
                ('resident', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apartment.resident')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
