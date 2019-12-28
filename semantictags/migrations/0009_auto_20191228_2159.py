# Generated by Django 2.1.3 on 2019-12-28 21:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('semantictags', '0008_tag_conflicts_with'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='labels',
            field=models.ManyToManyField(related_name='_tag_labels_+', to='semantictags.TagLabel'),
        ),
    ]
