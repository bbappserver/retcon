from django.db import models
from sharedstrings import Strings
# Create your models here.

class ManagedFile(models.Model):
    sha256 = models.BinaryField()

class Collection(models.Model):
    contents= models.ManyToManyField("ManagedFile",blank=True)
    parent = models.ForeignKey("self",null=True,blank=True,related_name="children",on_delete=models.DO_NOTHING)

class CollectionMetadata(models.Model):
    name= models.CharField(max_length=32)
    description= models.CharField(max_length=256)
    collection = models.OneToOneField("Collection",on_delete=models.CASCADE)
