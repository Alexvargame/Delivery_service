# Generated by Django 4.2.5 on 2023-10-03 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0005_order_order_number_alter_order_description_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_number',
            field=models.CharField(max_length=10, unique=True),
        ),
    ]