# Generated by Django 4.2.5 on 2023-10-09 07:41

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0012_alter_delivery_point_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='date_on_work',
            field=models.DateTimeField(default=datetime.datetime(2023, 10, 9, 11, 11, 10, 159022)),
        ),
        migrations.AlterField(
            model_name='delivery_point',
            name='building',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='delivery_point',
            name='office',
            field=models.CharField(blank=True, default=0, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='offices',
            name='building',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='offices',
            name='office',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='delivery_point',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, related_name='delivery_points', to='order.delivery_point'),
        ),
    ]