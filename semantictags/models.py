from django.db import models
from sharedstrings import models as sharedstrings
from django.db.models import Lookup
# Create your models here.



class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    labels = models.ManyToManyField("TagLabel",related_name="definitions")
    canonical_label = models.ForeignKey("TagLabel",null=True,blank=True,on_delete=models.DO_NOTHING,related_name="+")
    definition=models.CharField(max_length=256)

    def __str__(self):
        return "{}({}) - {}".format(self.canonical_label,self.id,self.definition)

class TagLabel(models.Model):
    label = models.CharField(max_length=64)
    language_code= models.ForeignKey("sharedstrings.Language",related_name="+",on_delete=models.DO_NOTHING)
    def __str__(self):
        return "{}".format(self.label)

class Taggable(models.Model):
    tags=models.ManyToManyField("semantictags.Tag")

    class Meta:
        abstract=True