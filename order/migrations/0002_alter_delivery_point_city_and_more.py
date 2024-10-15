# Generated by Django 4.2.5 on 2023-10-02 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='delivery_point',
            name='city',
            field=models.CharField(blank=True, choices=[('Харьков', 'Харьков')], max_length=100),
        ),
        migrations.AlterField(
            model_name='delivery_point',
            name='street',
            field=models.CharField(blank=True, choices=[('Гагарина проспект', 'Гагарина проспект'), ('Сумская', 'Сумская')], max_length=100),
        ),
        migrations.AlterField(
            model_name='offices',
            name='city',
            field=models.CharField(blank=True, choices=[('Харьков', 'Харьков')], max_length=100),
        ),
        migrations.AlterField(
            model_name='offices',
            name='street',
            field=models.CharField(blank=True, choices=[('Гагарина проспект', 'Гагарина проспект'), ('Сумская', 'Сумская')], max_length=100),
        ),
    ]
