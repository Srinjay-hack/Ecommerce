# Generated by Django 4.0.1 on 2022-01-12 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_items_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='items',
            name='discount_price',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
