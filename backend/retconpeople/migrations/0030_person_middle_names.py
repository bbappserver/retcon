# Generated by Django 2.2.14 on 2021-05-24 23:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('retconpeople', '0029_auto_20200828_0302'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='middle_names',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]
