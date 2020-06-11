from django.db import models
from sharedstrings.models import Strings
from .storage import HashStorage
from .fields import HashFileField
from retcon import settings
import binascii,os.path
# Create your models here.
class Filetype(models.Model):
    MIME = models.CharField(max_length=64)
    UTI= models.CharField(max_length=64,null=True,blank=True)

    def __str__(self):
        return self.MIME
    
    class Meta:
        ordering=('MIME',)
    
class NamedFile(models.Model):
    name=models.CharField(max_length=1024,null=True)
    inode=models.PositiveIntegerField(null=True,blank=True,default=None)
    identity=models.ForeignKey("ManagedFile",on_delete=models.CASCADE,null=True,related_name='names')

    def __str__(self):
        return self.name
    
    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]

class ManagedFile(models.Model):
    
    STORAGE_STATUS_MISSING='m'
    STORAGE_STATUS_HAVE='h'
    STORAGE_STATUS_DELETED='d'
    STORAGE_STATUS_CHOICES=(
        (STORAGE_STATUS_MISSING,'Missing'),
        (STORAGE_STATUS_HAVE,'Have'),
        (STORAGE_STATUS_DELETED,'Deleted')
    )
    md5=models.BinaryField(null=True,blank=True)
    sha256=models.BinaryField(null=True,blank=True)
    size=models.PositiveIntegerField(null=True,blank=True)
    storage_status=models.CharField(max_length=1,null=True,blank=True,choices=STORAGE_STATUS_CHOICES)
    retain_count=models.IntegerField(default=0,help_text="Positive indicates desire to keep, negative to delete,0=inbox")
    filetype = models.ForeignKey("Filetype",on_delete=models.PROTECT,null=True,blank=True,related_name='+')
    
    # def calculate_missing_hashes(self):
    @property
    def abspath(self):
        l_basename=self.sha.hex()
        l_dirname=l_basename[3]
        return os.path.join(settings.MANAGED_FILE_PATH,l_dirname,l_basename)

    def exists(self):
        e=os.path.exists(self.abspath)
        if not exists and self.STORAGE_STATUS_HAVE== self.storage_status:
            self.storage_status=self.STORAGE_STATUS_MISSING
            self.save()

    def open(self,mode='rb'):
        HashStorage().open(self.abspath,mode=mode)
    
    def track(self):
        if self.exists():
            return
        else:
            os.link(self.names[0],self.abspath)

    def delete(self):
        if self.exists():
            os.unlink(self.abspath)
        self.status=self.STORAGE_STATUS_DELETED
        self.save()
    
    def purge(self):
        for f in self.names:
            os.unlink(f)
        self.delete()
    
    @property
    def exists(self):
        HashStorage().exists(self.sha256)
    
    def __str__(self):
        # try:
        #     md5=binascii.hexlify(self.md5)
        # except:
        #     md5=None
        
        try:
            sha256=self.sha256.hex()
        except:
            sha256=None

        return 'sha256:{}'.format(sha256)
    
    class Meta:
        indexes = [models.Index(fields=['filetype'])]
    


class Collection(models.Model):
    contents= models.ManyToManyField("ManagedFile",blank=True)
    parents = models.ManyToManyField("self",blank=True,related_name="children")

class OrderedCollectionMembers(models.Model):
    managed_file= models.ForeignKey("ManagedFile",on_delete=models.CASCADE,related_name='+')
    collection= models.ForeignKey("Collection",on_delete=models.CASCADE,related_name="ordered_members")
    ordinal= models.PositiveSmallIntegerField()


class CollectionMetadata(models.Model):
    '''Optional minimal metadata for this collection'''
    name= models.CharField(max_length=64)
    description= models.CharField(max_length=256)
    collection = models.OneToOneField("Collection",on_delete=models.CASCADE,related_name='metadata')
