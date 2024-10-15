# Generated by Django 4.2.5 on 2023-10-02 11:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Город',
                'verbose_name_plural': 'Города',
            },
        ),
        migrations.CreateModel(
            name='Deliver',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Доставщик',
                'verbose_name_plural': 'Доставщики',
            },
        ),
        migrations.CreateModel(
            name='Delivery_point',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.CharField(blank=True, choices=[], max_length=100)),
                ('street', models.CharField(blank=True, choices=[], max_length=100)),
                ('building', models.CharField(blank=True, max_length=10)),
                ('office', models.CharField(blank=True, max_length=10)),
            ],
            options={
                'verbose_name': 'Адрес доставки',
                'verbose_name_plural': 'Адреса доставки',
            },
        ),
        migrations.CreateModel(
            name='Offices',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100)),
                ('city', models.CharField(blank=True, choices=[], max_length=100)),
                ('street', models.CharField(blank=True, choices=[], max_length=100)),
                ('building', models.CharField(blank=True, max_length=10)),
                ('office', models.CharField(blank=True, max_length=10)),
            ],
            options={
                'verbose_name': 'Адрес офиса',
                'verbose_name_plural': 'Адреса офисов',
            },
        ),
        migrations.CreateModel(
            name='Orderer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Заказчик',
                'verbose_name_plural': 'Заказчики',
            },
        ),
        migrations.CreateModel(
            name='Street',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Улица',
                'verbose_name_plural': 'Улицы',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('delivery_cost', models.FloatField()),
                ('description', models.TextField()),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('delivery_status', models.CharField(choices=[('delivered', 'delivered'), ('canceled', 'canceled')], max_length=20)),
                ('deliver', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='deliver', to='order.deliver')),
                ('delivery_point', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='delivery_points', to='order.delivery_point')),
                ('orderer', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='orderer', to='order.orderer')),
            ],
            options={
                'verbose_name': 'Заказ',
                'verbose_name_plural': 'Заказы',
            },
        ),
    ]
