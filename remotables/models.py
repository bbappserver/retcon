from django.db import models

# Create your models here.

class URL(models.model):
    url= models.CharField(max_length=512)
    represents = models.ForeignKey("RemoteEntity",related_name='urls',on_delete=models.DO_NOTHING)

class RemoteEntity(models.model):
    source_posted= models.DateTimeField(null=True)

class DynamicRemoteEntity(RemoteEntity):
    last_modified= models.DateTimeField(auto_now=True)
    local_created= models.DateTimeField(auto_now_add=True)