from django.db import models,transaction,IntegrityError
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


    @classmethod
    def prune_duplicates(cls):
        '''Not feasible forlarge numbers of files'''
        raise NotImplementedError()
        l=cls.objects.all().order_by('name', 'id')
        N=l.count()
        i=0
        j=i+1
        # from progress.bar import Bar
        # bar=Bar(max=N)
        while i < N:
            a=l[i]
            with transaction.atomic():
                j=i+1
                b=l[j]
                while a.name == b.name:
                    b.delete()
                    j+=1
                    # bar.next()
            i=j
            

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
    
    _write_once_fields=['md5','sha256','size']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self._write_once_fields:
            setattr(self, '__original_%s' % field, getattr(self, field))

    def _field_was_changed(self,field):
        orig = '__original_%s' % field
        if getattr(self, orig) != getattr(self, field):
            return True
        return False
    
    def _field_was_none(self,field):
        orig = '__original_%s' % field
        if getattr(self, orig) != getattr(self, field):
            return True
        return False

    def save(self, unsafe_modification=False, *args, **kwargs):
        '''Raises Integrity error if a write once field is modified.  Use unsafe_modification=True to override.'''
        is_update=self.pk is not None
        if not unsafe_modification and is_update:
            unsafe_fields=[]
            for f in self._write_once_fields:
                if self._field_was_changed(f) and not self._field_was_none(f):
                    unsafe_fields.append(f)
            if unsafe_fields:
                raise IntegrityError("The non-null fields {} cannot be modified.".format(unsafe_fields)) 
        else:
            super().save(*args, **kwargs)  # Call the "real" save() method.

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
            try:
                f.unlink()
            except FileNotFoundError:
                pass
        self.unlink()
    
    def retain(self):
        self.retain_count+=1
        self.save()
    
    def release(self):
        self.retain_count-=1
        self.save()

    @classmethod
    def get_or_create_from_blob(cls,blob):
        from hashlib import sha256,md5
        
        hasher=sha256()
        hasher_m=md5()
        for x in blob:
            hasher.update(x)
            hasher_m.update(x)
            
        dh=hasher.digest()
        dh_m=hasher_m.digest()
        
        o=cls.objects.filter(sha256=dh)
        if o.exists():
            o= o[0]
            if o.md5 is None:
                o.md5=dh_m
                o.save()
        else:
            o=cls(sha256=dh,md5=hasher_m.digest())
            o.save()
        
        return o
        
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

    @classmethod
    def run_autocorrelation(cls,tolerance=2):
        # grab all the hashes into a list (this takes a trivial maount of memory even for several million)
        l=list(Dhash.objects.all())
        N=l.count()

        #Broadphase
        for i in range(N):
            for j in range(i+1):
                x=l[i].dhash
                y=l[j].dhash
                z=x&y #bitwise and produces ony thos bits which are overlapped
                distance=count_bits(z)
                if distance < tolerance:
                    pass
                    #candidate for narrow phase
        
        #narrow phase
        #reduce so we only have to load any particular item for correlaiton once
        raise NotImplementedError()
        #CASE image match image
        #CASE image match video/animation
        #CASE video/animation match video/animation

        
        #Before saving always ensure the lower id is a and the higher is b
        if x.id<y.id:
            PerceptualMatch(a=x,b=y,type=match_type).save()
        else:
            PerceptualMatch(a=x,b=y,type=match_type).save()
    
    @classmethod
    def count_bits(cls,n):
        '''
        Integer sorcery counts bits efficiently in a 64 bit number
        https://stackoverflow.com/questions/9829578/fast-way-of-counting-non-zero-bits-in-positive-integer'''
        n = (n & 0x5555555555555555) + ((n & 0xAAAAAAAAAAAAAAAA) >> 1)
        n = (n & 0x3333333333333333) + ((n & 0xCCCCCCCCCCCCCCCC) >> 2)
        n = (n & 0x0F0F0F0F0F0F0F0F) + ((n & 0xF0F0F0F0F0F0F0F0) >> 4)
        n = (n & 0x00FF00FF00FF00FF) + ((n & 0xFF00FF00FF00FF00) >> 8)
        n = (n & 0x0000FFFF0000FFFF) + ((n & 0xFFFF0000FFFF0000) >> 16)
        n = (n & 0x00000000FFFFFFFF) + ((n & 0xFFFFFFFF00000000) >> 32) # This last & isn't strictly necessary.
        return n
# class PerceptualHash(Models.model):
#     class Meta:
#         abstract=True

#TODO the order of a hash inside a video file doesn't matter, but if a number of dhahses for a
#vide file, then proceed to narrow phase where you actually do a frame compare.

# class DHash(Models.model):
#     '''Perceptual hashes for broad phase perceptual matching
#     Actual file contents should be evaluated to calculate perceptual match'''
#     value=BigIntegerField()
#     managed_files= models.ManyToManyField("ManagedFile",related_name='dhashes')
