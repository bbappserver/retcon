# Generated by Django 2.1.3 on 2019-11-24 18:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('semantictags', '0007_auto_20191010_0008'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='conflicts_with',
            field=models.ManyToManyField(blank=True, help_text='&forall;x p(x) &harr; &not;q(x)', related_name='_tag_conflicts_with_+', to='semantictags.Tag'),
        ),
    ]