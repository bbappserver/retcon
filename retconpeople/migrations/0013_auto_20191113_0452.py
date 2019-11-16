# Generated by Django 2.1.1 on 2019-11-13 04:52

from django.db import migrations
import django.db.models.deletion
import sharedstrings.models


class Migration(migrations.Migration):

    dependencies = [
        ('retconpeople', '0012_auto_20191025_1332'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='first_name',
            field=sharedstrings.models.SharedStringField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='sharedstrings.Strings'),
        ),
        migrations.AlterField(
            model_name='person',
            name='last_name',
            field=sharedstrings.models.SharedStringField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='sharedstrings.Strings'),
        ),
        migrations.AlterField(
            model_name='username',
            name='name',
            field=sharedstrings.models.SharedStringField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='sharedstrings.Strings'),
        ),
        migrations.AlterField(
            model_name='website',
            name='name',
            field=sharedstrings.models.SharedStringField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='sharedstrings.Strings'),
        ),
        migrations.AlterField(
            model_name='website',
            name='tld',
            field=sharedstrings.models.SharedStringField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='sharedstrings.Strings'),
        ),
    ]