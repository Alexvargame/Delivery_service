# Generated by Django 4.2.5 on 2023-10-06 06:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0007_alter_order_deliver'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Deliver',
        ),
        migrations.AddField(
            model_name='delivery_point',
            name='name',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='offices',
            name='name',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]
