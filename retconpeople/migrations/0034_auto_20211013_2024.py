# Generated by Django 2.2.14 on 2021-10-13 20:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('retconpeople', '0033_website_owner'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='person',
            options={'ordering': ['id']},
        ),
        migrations.AlterField(
            model_name='username',
            name='wanted',
            field=models.BooleanField(blank=True, db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='usernumber',
            name='wanted',
            field=models.BooleanField(blank=True, db_index=True, null=True),
        ),
    ]