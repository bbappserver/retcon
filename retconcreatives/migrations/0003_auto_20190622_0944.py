# Generated by Django 2.1.3 on 2019-06-22 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('retconcreatives', '0002_auto_20190622_0943'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='actor',
            name='acted_in_movies',
        ),
        migrations.RemoveField(
            model_name='actor',
            name='acted_in_series',
        ),
        migrations.AddField(
            model_name='actor',
            name='acted_in',
            field=models.ManyToManyField(to='retconcreatives.Episode'),
        ),
    ]
