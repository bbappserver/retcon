# Generated by Django 2.2.28 on 2022-08-21 01:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('retconstorage', '0007_auto_20200612_2121'),
    ]

    operations = [
        migrations.CreateModel(
            name='Container',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1024)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='children', to='retconstorage.Container')),
            ],
            options={
                'unique_together': {('parent', 'name')},
            },
        ),
    ]
