# Generated by Django 4.2.5 on 2023-10-06 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0008_delete_deliver_delivery_point_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='street',
            name='city',
            field=models.CharField(blank=True, choices=[('Харьков', 'Харьков')], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='delivery_point',
            name='street',
            field=models.CharField(blank=True, choices=[], max_length=100),
        ),
        migrations.AlterField(
            model_name='offices',
            name='street',
            field=models.CharField(blank=True, choices=[], max_length=100),
        ),
    ]