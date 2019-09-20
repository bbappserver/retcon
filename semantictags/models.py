from django.db import models
from sharedstrings import models as sharedstrings
# Create your models here.

class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    labels = models.ManyToManyField("TagLabel",related_name="definitions")
    definition=models.CharField(max_length=256)

class TagLabel(models.Model):
    label = models.CharField(max_length=64)
    language_code= models.ForeignKey("sharedstrings.Language",related_name="+",on_delete=models.DO_NOTHING)

class Taggable(models.Model):
    tags=models.ManyToManyField("semantictags.Tag")

    class Meta:
        abstract=True