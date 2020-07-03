from django.db import models
from sharedstrings import models as sharedstrings
from django.db.models import Lookup
# Create your models here.



class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    labels = models.ManyToManyField("TagLabel",related_name="+")
    canonical_label = models.ForeignKey("TagLabel",null=True,blank=True,on_delete=models.DO_NOTHING,related_name="+")
    definition=models.CharField(max_length=256)
    implies = models.ManyToManyField("self",symmetrical=False,blank=True,related_name="implied_by",help_text="this &Implies; that")
    distinguish_from = models.ManyToManyField("self",symmetrical=True,blank=True, help_text="this ≠ that")
    conflicts_with = models.ManyToManyField("self",symmetrical=True,blank=True,help_text="x &#8853; y")

    def __str__(self):
        return "{}({}) - {}".format(self.canonical_label,self.id,self.definition)

class TagLabel(models.Model):
    label = models.CharField(max_length=64)
    language= models.ForeignKey("sharedstrings.Language",related_name="+",on_delete=models.DO_NOTHING)
    
    @property
    def definitions(self):
        return Tag.objects.filter(labels=self) | Tag.objects.filter(canonical_label=self)

    def __str__(self):
        return "{}.{}".format(self.language.isocode,self.label)

class Taggable(models.Model):
    tags=models.ManyToManyField("semantictags.Tag",blank=True)
    ambiguous_tags=models.ManyToManyField("sharedstrings.Strings",blank=True,related_name="+")

    class Meta:
        abstract=True