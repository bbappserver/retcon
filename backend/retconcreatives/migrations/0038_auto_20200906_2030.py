# Generated by Django 2.2.14 on 2020-09-06 20:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sharedstrings', '0008_merge_20191124_1653'),
        ('retconcreatives', '0037_auto_20200828_0302'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='title',
            unique_together={('name', 'language', 'creative_work')},
        ),
    ]
