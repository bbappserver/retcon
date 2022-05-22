from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import UploadedFile
from django.db.models.fields.files import FieldFile
import os.path
import shutil
from django.utils.deconstruct import deconstructible



#from .models import ManagedFile
@deconstructible
class HashStorage(FileSystemStorage):

    _default={'root':'_data'}
    def __init__(self, option=None):
        if not option:
            self.option = getattr(settings,'CUSTOM_STORAGE_OPTIONS',self._default)
        self.mkdirs_mask=0o755
        self.relocation_method='move'

    def _open(self,name,mode='rb'):
        if isinstance(name, (bytes, bytearray)):
            name = hex(name)
        return open(self._internal_path(name),mode=mode)
    
    def _abs_path(self,relpath):
        return os.path.join(settings.BASE_DIR,self.option['root'],relpath)


    def _internal_path(self,hash):
        prefix=hash[0:3]
        d=self._abs_path(prefix)
        return d


    def _save_internal(self,hash,content):
        if isinstance(hash, (bytes, bytearray)):
            hash = hex(hash)
        d= self._internal_path(hash)
        os.makedirs(d,exist_ok=True)
        p=os.path.join(d,hash)
        
        old = content
        content.name=hash
        if isinstance(content,UploadedFile):
            with open(p,'wb') as f:
                for c in content.chunks():
                    f.write(c)
            return
            

        
        if self.relocation_method == "move":
            shutil.move(old,p)
        elif self.relocation_method == "link":
            os.link(old,p)
        elif self.relocation_method == "copy":
            shutil.copyfile(old,p)
        elif self.relocation_method == "ref":
            try:
                from reflink import reflink
                reflink(old, p)
            except ImportError as e:
                print("You need the reflink model to use reflink mode hash storage\n\t pip3 install reflink")
                raise e
            except OSError as e:
                raise e

    def _save(self,name,content,max_length=None):
        import hashlib
        data = content.read() # read entire file as bytes
        hasher=hashlib.sha256(data)
        readable_hash = hasher.hexdigest()
        binary_hash = hasher.digest()
        self._save_internal(readable_hash,content)

        #We want the filefield to use the compressed representatiob
        #
        return readable_hash
    
    def delete(self,name):
        #delete file
        #mark record deleted
        raise NotImplementedError()
    
    def exists(self,name):
        return os.path.exists(self._internal_path(name))
    
    def get_accessed_time(self,name):
        raise NotImplementedError()
    

