# Generated by Django 2.2.28 on 2023-07-15 00:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('retconstorage', '0008_container'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='parents',
            field=models.ManyToManyField(blank=True, related_name='children', to='retconstorage.Collection'),
        ),
    ]
