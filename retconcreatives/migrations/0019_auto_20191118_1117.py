# Generated by Django 2.1.3 on 2019-11-18 11:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('retconpeople', '0013_auto_20191118_1107'),
        ('retconcreatives', '0018_auto_20191118_1107'),
    ]

    operations = [
        migrations.AddField(
            model_name='creativework',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='retconpeople.Person'),
        ),
        migrations.AlterField(
            model_name='creativework',
            name='published_on',
            field=models.DateField(blank=True, null=True),
        ),
    ]
