# Generated by Django 2.2.14 on 2020-08-28 03:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('remotables', '0003_auto_20200731_0815'),
        ('retconcreatives', '0036_auto_20200828_0235'),
    ]

    operations = [
        migrations.RenameField(
            model_name='company',
            old_name='external_representation',
            new_name='external_representations'
        ),
        migrations.RenameField(
            model_name='creativework',
            old_name='external_representation',
            new_name='external_representations'
        ),
    ]