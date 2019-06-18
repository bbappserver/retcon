from django.db import models
from sharedstrings import models as sharedstrings
# Create your models here.

class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    labels = models.ForeignKey("TagLabel",related_name="definitions",on_delete=models.DO_NOTHING)
    definition=models.CharField(max_length=256)

class TagLabel(models.Model):
    label = models.ForeignKey("sharedstrings.Strings",related_name="+",on_delete=models.DO_NOTHING)
    language_code= models.ForeignKey("sharedstrings.Strings",related_name="+",on_delete=models.DO_NOTHING)