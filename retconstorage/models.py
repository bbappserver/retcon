from django.db import models
from sharedstrings.models import Strings
from .storage import HashStorage
from .fields import HashFileField
from retcon import settings
import binascii,os.path,unicodedata
import sys
is_macos = sys.platform=='darwin'


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
    
    def display_size(self):
        if self.identity is None or self.identity.size is None:
            return "?"
        return "{:.2f} MiB".format(self.identity.size/(1<<20))
    def display_MIME(self):
        if self.identity is None or self.identity.filetype is None:
            return "?"
        return self.identity.filetype.MIME
    
    def multiplicity(self):
        if self.identity is None:
            return "?"
        n=self.identity.names.count()
        return n if n>0 else "? 1"
    def deduped_multiplicity(self):
        if self.identity is None:
            return "?"
        n= len(set((x.inode for x in self.identity.names.all())))
        return n if n>0 else "? 1"

    def alternate_names(self):
        return [x.name for x in self.identity.names.all()]

    @property
    def abspath(self,prefix=settings.NAMED_FILE_PREFIX):
        p= os.path.join(prefix,self.name)
        if is_macos:
            return unicodedata.normalize('NFC', p)
        else:
            return unicodedata.normalize('NFD', p)
    
    @property
    def exists(self):
        return os.path.exists(self.abspath)
    
    def stat(self,prefix=settings.NAMED_FILE_PREFIX):
        return os.stat(self._abspath(prefix))
    
    def unlink(self):
        return os.unlink(self.abspath)

    def _abspath(self,prefix=settings.NAMED_FILE_PREFIX):
        return os.path.join(prefix,self.name)


    class Meta:
        unique_together=(
            ("name","inode")
        )

class ManagedFile(models.Model):
    
    STORAGE_STATUS_MISSING='m'
    STORAGE_STATUS_HAVE='h'
    STORAGE_STATUS_DELETED='d'
    STORAGE_STATUS_CHOICES=(
        (STORAGE_STATUS_MISSING,'Missing'),
        (STORAGE_STATUS_HAVE,'Have'),
        (STORAGE_STATUS_DELETED,'Deleted')
    )
    md5=models.BinaryField(null=True,blank=True,unique=True)
    sha256=models.BinaryField(null=True,blank=True,unique=True)
    size=models.PositiveIntegerField(null=True,blank=True)
    storage_status=models.CharField(max_length=1,null=True,blank=True,choices=STORAGE_STATUS_CHOICES)
    retain_count=models.IntegerField(default=0,help_text="Positive indicates desire to keep, negative to delete,0=inbox")
    filetype = models.ForeignKey("Filetype",on_delete=models.PROTECT,null=True,blank=True,related_name='+')
    
    # def calculate_missing_hashes(self):
    def robust_abspath(self):
        '''Returns a tracked path or the first named file that exists'''
        p=self.abspath
        if os.path.exists(p):
            return p
        else:
            for nf in self.names:
                p = n.abspath
                if os.path.exists(p):
                    return p
    
    def robust_stat(self):
        '''Return the stat structure for a tracked path or the first named file that exists'''
        managed_path=self.abspath
        #did it this way to save the work of calculating a lot of abs path since this could be called often
        if os.path.exists(managed_path):
            return os.stat(managed_path)
        else:
            for nf in self.names.all():
                if nf.exists:
                    return nf.stat()




    @property
    def abspath(self):
        l_basename=self.sha256.hex()
        l_dirname=l_basename[:3]
        return os.path.join(settings.MANAGED_FILE_PATH,l_dirname,l_basename)

    @property
    def exists(self):
        e=os.path.exists(self.abspath)
        return e
        # if not exists and self.STORAGE_STATUS_HAVE== self.storage_status:
        #     self.storage_status=self.STORAGE_STATUS_MISSING
        #     self.save()

    @property
    def isTracked(self):
        return self.storage_status is not None
    def open(self,mode='rb'):
        HashStorage().open(self.abspath,mode=mode)
    
    def track(self):
        if not self.exists:
            os.link(self.robust_abspath(),self.abspath)
        self.storage_status=STORAGE_STATUS_HAVE 

    def unlink(self):
        if self.exists:
            os.unlink(self.abspath)
        self.status=self.STORAGE_STATUS_DELETED
        self.save()
    
    def purge(self):
        for f in self.names.all():
            f.unlink()
        self.unlink()
    
    def strnames(self):
        return [x.name for x in self.names.all()]
    
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

# class PerceptualMatch(models.model):

#     '''Storages for matches of images (sequences of length 1), and image sequences including animated gif and movies''' 
#     MATCH_TYPE_EQ=0 #The sequences match
#     MATCH_TYPE_A_ISSUBSETOF_B=1 #Sequence A is embeded in B
#     MATCH_TYPE_A_ISSUPERSET_B=2 #Sequence B is embeded in A
#     MATCH_TYPE_A_PREFIXES_B=3 #Sequence A doesn't overlap and then overlaps B
#     MATCH_TYPE_A_SUFFIXES_B=4 #Sequence A overlaps and then doesn't overlap B
#     MATCH_TYPE_A_PARTIALLY_PREFIXES_B=5 #Sequence A doesn't overlap and then partially overlaps B
#     MATCH_TYPE_A_PARTIALLY_SUFFIXES_B=6 #Sequence A partially overlaps and then doesn't overlap B
#     MATCH_TYPE_RANDOM_SUBSET=7 #The sequences seem overlapped in no descernable pattern
    
#     MATCH_TYPE_CHOICES=[]

#     a=models.ForeignKey('ManagedFile')
#     b=models.ForeignKey('ManagedFile')
#     type=models.CharField(max_length=1,choices=MATCH_TYPE_CHOICES)
# class PerceptualHash(Models.model):
#     class Meta:
#         abstract=True

#TODO the order of a hash inside a video file doesn't matter, but if a number of dhahses for a
#vide file, then proceed to narrow phase where you actually do a frame compare.

# class DHash(Models.model):
#     '''Perceptual hashes for broad phase perceptual matching
#     Actual file contents should be evaluated to calculate perceptual match'''
#     managed_file= models.ForeignKey("ManagedFile",on_delete=models.CASCADE,related_name='+')
# #    hash= 
