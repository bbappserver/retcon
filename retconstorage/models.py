from django.db import models
from sharedstrings.models import Strings
from .storage import HashStorage
from .fields import HashFileField
import binascii
# Create your models here.
class Filetype(models.Model):
    MIME = models.CharField(max_length=64)
    UTI= models.CharField(max_length=64,null=True,blank=True)

class ManagedFile(models.Model):
    #file = HashFileField()
    md5=models.BinaryField(null=True,blank=True)
    sha256=models.BinaryField(null=True,blank=True)
    filetype = models.ForeignKey("Filetype",on_delete=models.PROTECT,null=True,blank=True)
    
    # def calculate_missing_hashes(self):

    def open(self,mode='rb'):
        HashStorage().open(self.sha256,mode=mode)
    
    @property
    def exists(self):
        HashStorage().exists(self.sha256)
    
    def __str__(self):
        # try:
        #     md5=binascii.hexlify(self.md5)
        # except:
        #     md5=None
        
        try:
            sha256=binascii.hexlify(self.sha256)
        except:
            sha256=None
        return 'sha256:%s' %(sha256,)
    


class Collection(models.Model):
    contents= models.ManyToManyField("ManagedFile",blank=True)
    parents = models.ManyToManyField("self",blank=True,related_name="children")

class CollectionMetadata(models.Model):
    name= models.CharField(max_length=64)
    description= models.CharField(max_length=256)
    collection = models.OneToOneField("Collection",on_delete=models.CASCADE,related_name='metadata')
