# Generated by Django 2.2.28 on 2023-07-19 02:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('retconstorage', '0010_auto_20230719_0218'),
        ('retconcreatives', '0042_episode_production_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='creativework',
            name='represents_collections',
            field=models.ManyToManyField(to='retconstorage.Collection',blank=True),
        ),
    ]
