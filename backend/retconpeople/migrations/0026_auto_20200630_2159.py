# Generated by Django 2.1.3 on 2020-06-30 21:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('retconpeople', '0025_transfer_url_patterns'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='website',
            name='user_number_pattern',
        ),
        migrations.RemoveField(
            model_name='website',
            name='username_pattern',
        ),
        migrations.AddField(
            model_name='website',
            name='user_id_format_string',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
    ]