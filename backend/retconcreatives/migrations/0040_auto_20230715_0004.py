# Generated by Django 2.2.28 on 2023-07-15 00:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('retconcreatives', '0039_remove_company_website'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='is_favourite',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='company',
            name='notes',
            field=models.TextField(default=None, max_length=512, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='creativework',
            name='is_favourite',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='creativework',
            name='notes',
            field=models.TextField(default=None, max_length=512, null=True, blank=True),
        ),
    ]
