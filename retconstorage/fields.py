import datetime
import posixpath
import binascii

from django import forms
from django.core import checks
from django.core.files.base import File
from django.core.files.images import ImageFile
from django.core.files.storage import default_storage
from django.db.models import signals
from django.db.models.fields.files import *

from .storage import HashStorage

class HashFileField(FileField):

    # The class to wrap instance attributes in. Accessing the file object off
    # the instance will always return an instance of attr_class.
    attr_class = FieldFile

    # The descriptor to use for accessing the attribute off of the class.
    descriptor_class = FileDescriptor

    description = ("File")

    def __init__(self, filename_encoder=binascii.hexlify,filename_decoder=binascii.unhexlify, **kwargs):
        if 'storage' not in kwargs: kwargs['storage'] = HashStorage() 
        super().__init__(**kwargs)
        self.filename_encoder=filename_encoder
        self.filename_decoder=filename_decoder
        

    
    def get_internal_type(self):
        return "BinaryField"

    def get_prep_value(self, value):
        if isinstance(value,FieldFile):
            value=value.name
        if isinstance(value,str):
            value = self.filename_decoder(value)
            
        return super().get_prep_value(value)
    
    def to_python(self, value):
        if isinstance(value, str):
            return value

        if value is None:
            return value

        if isinstance(value,File):
            return value

        return self.filename_decoder(value)
        

    # def pre_save(self, model_instance, add):
    #     file = super().pre_save(model_instance, add)
    #     if file and not file._committed:
    #         # Commit the file to storage prior to saving the model
    #         file.save(file.name, file.file, save=False)
    #     return file

    # def contribute_to_class(self, cls, name, **kwargs):
    #     super().contribute_to_class(cls, name, **kwargs)
    #     setattr(cls, self.name, self.descriptor_class(self))

    # def generate_filename(self, instance, filename):
    #     """
    #     Apply (if callable) or prepend (if a string) upload_to to the filename,
    #     then delegate further processing of the name to the storage backend.
    #     Until the storage layer, all file paths are expected to be Unix style
    #     (with forward slashes).
    #     """
    #     if callable(self.upload_to):
    #         filename = self.upload_to(instance, filename)
    #     else:
    #         dirname = datetime.datetime.now().strftime(self.upload_to)
    #         filename = posixpath.join(dirname, filename)
    #     return self.storage.generate_filename(filename)

    # def save_form_data(self, instance, data):
    #     # Important: None means "no change", other false value means "clear"
    #     # This subtle distinction (rather than a more explicit marker) is
    #     # needed because we need to consume values that are also sane for a
    #     # regular (non Model-) Form to find in its cleaned_data dictionary.
    #     if data is not None:
    #         # This value will be converted to str and stored in the
    #         # database, so leaving False as-is is not acceptable.
    #         setattr(instance, self.name, data or '')

    # def formfield(self, **kwargs):
    #     return super().formfield(**{
    #         'form_class': forms.FileField,
    #         'max_length': self.max_length,
    #         **kwargs,
    #     })