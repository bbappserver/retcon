# Generated by Django 2.1.3 on 2020-06-12 21:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('retconstorage', '0006_orderedcollectionmembers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='managedfile',
            name='md5',
            field=models.BinaryField(blank=True, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='managedfile',
            name='sha256',
            field=models.BinaryField(blank=True, null=True, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='namedfile',
            unique_together={('name', 'inode')},
        ),
    ]
