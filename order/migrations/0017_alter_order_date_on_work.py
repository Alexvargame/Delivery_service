# Generated by Django 4.2.5 on 2023-10-12 12:39

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0016_alter_delivery_point_city_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='date_on_work',
            field=models.DateTimeField(default=datetime.datetime(2023, 10, 12, 16, 9, 56, 924397)),
        ),
    ]
