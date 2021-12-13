# Generated by Django 2.2.14 on 2021-05-24 23:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('remotables', '0005_auto_20200906_2030'),
        ('retconpeople', '0030_person_middle_names'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='in_photos',
            field=models.ManyToManyField(blank=True, related_name='_person_in_photos_+', to='remotables.ContentResource'),
        ),
        migrations.AddField(
            model_name='person',
            name='potentially_in_photos',
            field=models.ManyToManyField(blank=True, related_name='_person_potentially_in_photos_+', to='remotables.ContentResource'),
        ),
        migrations.AddField(
            model_name='person',
            name='solo_photos',
            field=models.ManyToManyField(blank=True, related_name='_person_solo_photos_+', to='remotables.ContentResource'),
        ),
    ]