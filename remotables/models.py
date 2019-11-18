from django.db import models

# Create your models here.
# class URLScheme(models.model):
#     name=models.CharField(max_length=16)
# class Hostname(models.model):
#     name=models.CharField(max_length=16)

class URL(models.model):
    url= models.CharField(max_length=512)
    represents = models.ForeignKey("RemoteEntity",related_name='urls',on_delete=models.DO_NOTHING)

class EphemeralUrl(URL):
    '''Lots of URLS are temporary tokens valid for a short persiod put those here'''
    valid_until =  models.DateTimeField()

class RemoteEntity(models.model):
    '''Particular metadata about an entity a URL represents'''
    source_posted= models.DateTimeField(null=True)

class DynamicRemoteEntity(RemoteEntity):
    '''Lots of entities are not static, for non static entities use this'''
    last_modified= models.DateTimeField(auto_now=True)
    local_created= models.DateTimeField(auto_now_add=True)